"""Payment and code management routes.

Endpoints:
    GET    /codes/packages           - List available packages + prices (public)
    POST   /codes/purchase           - Create Stripe checkout session
    POST   /codes/dev-purchase       - Dev-only: generate codes without Stripe
    POST   /codes/webhook            - Stripe webhook handler (no auth, sig verified)
    GET    /codes/my-codes           - List user's purchased/assigned codes
    POST   /codes/redeem             - Redeem a code (activate token for user)
    GET    /codes/purchase/{id}      - Get purchase status + generated codes
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.models.user import User
from bfg_core.models.token import DiagnosticToken, TokenStatus
from bfg_core.models.purchase import CodePurchase, CodePackageType
from bfg_core.services.stripe_service import StripeService, get_package_info, PACKAGES
from bfg_core.services.token_service import TokenService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class PurchaseRequest(BaseModel):
    package_type: str  # "single", "pack_10", etc.


class RedeemRequest(BaseModel):
    code: str


class PackageResponse(BaseModel):
    type: str
    quantity: int
    unit_price_cents: int
    total_price_cents: int
    label: str
    savings_percent: int


class CodeResponse(BaseModel):
    id: str
    token_code: str
    status: str
    diagnostic_type: str
    tier: str
    created_at: str
    activated_at: str | None = None
    consumed_at: str | None = None
    expires_at: str | None = None


class PurchaseDetailResponse(BaseModel):
    id: str
    package_type: str
    quantity: int
    total_price_cents: int
    status: str
    codes: list[CodeResponse]
    created_at: str
    completed_at: str | None = None


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_payment_routes(
    get_db,
    get_current_user,
    stripe_service,
    token_service,
):
    """Factory to create payment/code routes with injected dependencies.

    stripe_service and token_service can be callables (lazy init) or direct instances.
    """
    router = APIRouter(prefix="/codes", tags=["codes"])

    def _stripe() -> StripeService:
        return stripe_service() if callable(stripe_service) else stripe_service

    def _tokens() -> TokenService:
        return token_service() if callable(token_service) else token_service

    @router.get("/packages", response_model=list[PackageResponse])
    async def list_packages():
        """List available code packages with prices. Public endpoint."""
        return [get_package_info(pkg_type) for pkg_type in PACKAGES]

    @router.post("/purchase")
    async def create_purchase(
        body: PurchaseRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Create a Stripe Checkout Session for code purchase.

        Returns checkout_url for redirect to Stripe.
        """
        try:
            package_type = CodePackageType(body.package_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Ungueltiger Pakettyp: {body.package_type}",
            )

        if not _stripe().is_configured:
            raise HTTPException(
                status_code=503,
                detail="Zahlungssystem nicht konfiguriert. Bitte kontaktiere den Support.",
            )

        try:
            result = await _stripe().create_checkout_session(
                buyer_id=user.id,
                package_type=package_type,
                db=db,
            )
            return result
        except Exception as e:
            logger.exception("Stripe checkout creation failed")
            raise HTTPException(
                status_code=500,
                detail="Fehler beim Erstellen der Checkout-Session.",
            )

    @router.post("/dev-purchase")
    async def create_dev_purchase(
        body: PurchaseRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Development-only: Generate codes without Stripe payment.

        Only available when ENVIRONMENT=development.
        """
        from app.config import settings
        if settings.environment != "development":
            raise HTTPException(status_code=403, detail="Only available in development mode")

        try:
            package_type = CodePackageType(body.package_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Ungueltiger Pakettyp: {body.package_type}",
            )

        purchase = await _stripe().create_dev_purchase(
            buyer_id=user.id,
            package_type=package_type,
            db=db,
        )

        # Load the generated tokens and auto-activate all for the buyer
        codes = []
        if purchase.token_ids:
            for tid in purchase.token_ids:
                result = await db.execute(
                    select(DiagnosticToken).where(DiagnosticToken.id == UUID(tid))
                )
                token = result.scalar_one_or_none()
                if token:
                    # Auto-activate for the purchasing user (dev convenience)
                    try:
                        token = await _tokens().activate_token(token.token_code, user.id)
                    except ValueError as e:
                        logger.warning("Auto-activate failed for token %s: %s", tid, e)
                    codes.append(_token_to_response(token))

        return PurchaseDetailResponse(
            id=str(purchase.id),
            package_type=purchase.package_type.value,
            quantity=purchase.quantity,
            total_price_cents=purchase.total_price_cents,
            status=purchase.status.value,
            codes=codes,
            created_at=purchase.created_at.isoformat(),
            completed_at=purchase.completed_at.isoformat() if purchase.completed_at else None,
        )

    @router.post("/webhook")
    async def stripe_webhook(
        request: Request,
        db: AsyncSession = Depends(get_db),
    ):
        """Stripe webhook handler. No auth — uses webhook signature verification."""
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")

        try:
            purchase = await _stripe().handle_webhook(payload, sig_header, db)
            return {"status": "ok", "purchase_id": str(purchase.id) if purchase else None}
        except ValueError as e:
            logger.warning("Webhook validation failed: %s", e)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            logger.exception("Webhook processing failed")
            raise HTTPException(status_code=500, detail="Webhook processing error")

    @router.get("/my-codes", response_model=list[CodeResponse])
    async def list_my_codes(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """List all diagnostic codes owned by the current user."""
        tokens = await _tokens().get_user_tokens(user.id)

        # Also get tokens sold by this user (coach buying codes)
        result = await db.execute(
            select(DiagnosticToken)
            .where(DiagnosticToken.sold_by_expert_id == user.id)
            .order_by(DiagnosticToken.created_at.desc())
        )
        sold_tokens = list(result.scalars().all())

        # Merge and deduplicate
        all_tokens = {str(t.id): t for t in tokens}
        for t in sold_tokens:
            all_tokens[str(t.id)] = t

        return [_token_to_response(t) for t in all_tokens.values()]

    @router.post("/redeem")
    async def redeem_code(
        body: RedeemRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Activate a diagnostic code for the current user.

        The code must be in EMITTED, SOLD, or ASSIGNED status.
        After activation, it can be used to start a diagnostic session.
        """
        try:
            token = await _tokens().activate_token(body.code, user.id)
            return {
                "status": "activated",
                "token_code": token.token_code,
                "message": "Code erfolgreich eingeloest! Du kannst jetzt eine Diagnostik starten.",
            }
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Code konnte nicht eingeloest werden: {str(e)}",
            )

    @router.post("/activate/{code_id}")
    async def activate_code(
        code_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Activate a specific code by ID for the current user.

        Unlike /redeem (which takes a code string), this takes the code UUID
        and is used from the codes management page.
        """
        result = await db.execute(
            select(DiagnosticToken).where(DiagnosticToken.id == code_id)
        )
        token = result.scalar_one_or_none()
        if not token:
            raise HTTPException(status_code=404, detail="Code nicht gefunden")

        # Verify ownership: user must be the buyer (sold_by_expert_id) or
        # the code must be unowned
        if (
            token.sold_by_expert_id != user.id
            and token.user_id is not None
            and token.user_id != user.id
        ):
            raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Code")

        try:
            activated = await _tokens().activate_token(token.token_code, user.id)
            return {
                "status": "activated",
                "token_code": activated.token_code,
                "message": "Code aktiviert! Du kannst jetzt eine Diagnostik starten.",
            }
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Code konnte nicht aktiviert werden: {str(e)}",
            )

    @router.get("/purchase/{purchase_id}", response_model=PurchaseDetailResponse)
    async def get_purchase_status(
        purchase_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get purchase details and associated codes."""
        result = await db.execute(
            select(CodePurchase).where(
                CodePurchase.id == purchase_id,
                CodePurchase.buyer_id == user.id,
            )
        )
        purchase = result.scalar_one_or_none()
        if not purchase:
            raise HTTPException(status_code=404, detail="Kauf nicht gefunden")

        # Load associated tokens
        codes = []
        if purchase.token_ids:
            for tid in purchase.token_ids:
                result = await db.execute(
                    select(DiagnosticToken).where(DiagnosticToken.id == UUID(tid))
                )
                token = result.scalar_one_or_none()
                if token:
                    codes.append(_token_to_response(token))

        return PurchaseDetailResponse(
            id=str(purchase.id),
            package_type=purchase.package_type.value,
            quantity=purchase.quantity,
            total_price_cents=purchase.total_price_cents,
            status=purchase.status.value,
            codes=codes,
            created_at=purchase.created_at.isoformat(),
            completed_at=purchase.completed_at.isoformat() if purchase.completed_at else None,
        )

    def _token_to_response(token: DiagnosticToken) -> CodeResponse:
        """Convert a DiagnosticToken to a CodeResponse."""
        return CodeResponse(
            id=str(token.id),
            token_code=token.token_code,
            status=token.status.value,
            diagnostic_type=token.diagnostic_type,
            tier=token.tier.value,
            created_at=token.created_at.isoformat(),
            activated_at=token.activated_at.isoformat() if token.activated_at else None,
            consumed_at=token.consumed_at.isoformat() if token.consumed_at else None,
            expires_at=token.expires_at.isoformat() if token.expires_at else None,
        )

    return router
