"""Stripe payment service — Checkout Sessions for code purchases.

Handles the full payment flow:
    1. Coach/user selects package → create_checkout_session()
    2. Stripe redirects after payment → webhook confirms
    3. handle_webhook() → generates diagnostic tokens

Usage:
    svc = StripeService(settings, token_service)
    result = await svc.create_checkout_session(user_id, CodePackageType.PACK_10, db)
    # result = {"checkout_url": "https://checkout.stripe.com/...", ...}
"""

import logging
from datetime import datetime
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.config import CoreSettings
from bfg_core.models.purchase import CodePurchase, PurchaseStatus, CodePackageType
from bfg_core.models.token import TokenTier
from bfg_core.services.token_service import TokenService

logger = logging.getLogger(__name__)

# Package definitions: type → (quantity, unit_price_cents, label_de)
PACKAGES: dict[CodePackageType, tuple[int, int, str]] = {
    CodePackageType.SINGLE: (1, 4900, "SCIL Diagnostik-Code (Einzeln)"),
    CodePackageType.PACK_10: (10, 4400, "SCIL Diagnostik-Codes (10er-Paket)"),
    CodePackageType.PACK_25: (25, 3900, "SCIL Diagnostik-Codes (25er-Paket)"),
    CodePackageType.PACK_50: (50, 3400, "SCIL Diagnostik-Codes (50er-Paket)"),
    CodePackageType.PACK_100: (100, 2900, "SCIL Diagnostik-Codes (100er-Paket)"),
}


def get_package_info(package_type: CodePackageType) -> dict:
    """Get package details including savings percentage."""
    qty, unit_price, label = PACKAGES[package_type]
    base_price = PACKAGES[CodePackageType.SINGLE][1]  # single code price
    savings = round((1 - unit_price / base_price) * 100) if qty > 1 else 0
    return {
        "type": package_type.value,
        "quantity": qty,
        "unit_price_cents": unit_price,
        "total_price_cents": qty * unit_price,
        "label": label,
        "savings_percent": savings,
    }


class StripeService:
    """Manages Stripe Checkout Sessions for code purchases."""

    def __init__(self, settings: CoreSettings, token_service: TokenService):
        self._settings = settings
        self._token_service = token_service
        if settings.stripe_secret_key:
            stripe.api_key = settings.stripe_secret_key

    @property
    def is_configured(self) -> bool:
        """Check if Stripe is properly configured."""
        return bool(self._settings.stripe_secret_key)

    async def create_checkout_session(
        self,
        buyer_id: UUID,
        package_type: CodePackageType,
        db: AsyncSession,
    ) -> dict:
        """Create a Stripe Checkout Session and a pending CodePurchase record.

        Returns:
            {"checkout_url": str, "session_id": str, "purchase_id": str}
        """
        if not self.is_configured:
            raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY.")

        qty, unit_price, label = PACKAGES[package_type]
        total = qty * unit_price

        # Create pending purchase record
        purchase = CodePurchase(
            buyer_id=buyer_id,
            package_type=package_type,
            quantity=qty,
            unit_price_cents=unit_price,
            total_price_cents=total,
        )
        db.add(purchase)
        await db.flush()

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": label},
                        "unit_amount": unit_price,
                    },
                    "quantity": qty,
                }
            ],
            mode="payment",
            success_url=(
                f"{self._settings.frontend_url}/codes/success"
                f"?purchase_id={purchase.id}"
            ),
            cancel_url=f"{self._settings.frontend_url}/codes/cancel",
            metadata={
                "purchase_id": str(purchase.id),
                "buyer_id": str(buyer_id),
                "package_type": package_type.value,
            },
        )

        purchase.stripe_session_id = checkout_session.id
        await db.commit()

        logger.info(
            "Checkout session created: purchase=%s package=%s qty=%d",
            purchase.id,
            package_type.value,
            qty,
        )

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "purchase_id": str(purchase.id),
        }

    async def handle_webhook(
        self,
        payload: bytes,
        sig_header: str,
        db: AsyncSession,
    ) -> CodePurchase | None:
        """Process Stripe webhook event.

        Returns completed CodePurchase on success, None for irrelevant events.
        """
        if not self._settings.stripe_webhook_secret:
            raise ValueError("Stripe webhook secret not configured.")

        event = stripe.Webhook.construct_event(
            payload, sig_header, self._settings.stripe_webhook_secret
        )

        if event["type"] == "checkout.session.completed":
            session_data = event["data"]["object"]
            return await self._fulfill_purchase(session_data, db)

        logger.debug("Ignored Stripe event: %s", event["type"])
        return None

    async def _fulfill_purchase(
        self,
        stripe_session: dict,
        db: AsyncSession,
    ) -> CodePurchase:
        """Generate diagnostic tokens after successful payment.

        Idempotent — safe to call multiple times for the same purchase.
        """
        purchase_id = stripe_session["metadata"]["purchase_id"]

        result = await db.execute(
            select(CodePurchase).where(CodePurchase.id == UUID(purchase_id))
        )
        purchase = result.scalar_one_or_none()
        if not purchase:
            raise ValueError(f"Purchase not found: {purchase_id}")

        # Idempotency check
        if purchase.status == PurchaseStatus.COMPLETED:
            logger.info("Purchase already fulfilled: %s", purchase_id)
            return purchase

        try:
            # Generate tokens via existing TokenService
            tokens = await self._token_service.generate_token(
                tier=TokenTier.M,
                diagnostic_type="scil",
                quantity=purchase.quantity,
                sold_by_expert_id=purchase.buyer_id,
                purchase_price=purchase.unit_price_cents / 100,
                retail_price=purchase.unit_price_cents / 100,
            )

            purchase.stripe_payment_intent_id = stripe_session.get("payment_intent")
            purchase.status = PurchaseStatus.COMPLETED
            purchase.token_ids = [str(t.id) for t in tokens]
            purchase.completed_at = datetime.utcnow()

            await db.commit()

            logger.info(
                "Purchase fulfilled: %s → %d tokens generated",
                purchase_id,
                len(tokens),
            )
        except Exception:
            purchase.status = PurchaseStatus.FAILED
            await db.commit()
            logger.exception("Failed to fulfill purchase: %s", purchase_id)
            raise

        return purchase

    async def create_dev_purchase(
        self,
        buyer_id: UUID,
        package_type: CodePackageType,
        db: AsyncSession,
    ) -> CodePurchase:
        """Development-only: Create a completed purchase without Stripe.

        Useful for testing when Stripe is not configured.
        Directly generates tokens and marks purchase as completed.
        """
        qty, unit_price, label = PACKAGES[package_type]
        total = qty * unit_price

        # Generate tokens
        tokens = await self._token_service.generate_token(
            tier=TokenTier.M,
            diagnostic_type="scil",
            quantity=qty,
            sold_by_expert_id=buyer_id,
            purchase_price=unit_price / 100,
            retail_price=unit_price / 100,
        )

        # Create completed purchase record
        purchase = CodePurchase(
            buyer_id=buyer_id,
            package_type=package_type,
            quantity=qty,
            unit_price_cents=unit_price,
            total_price_cents=total,
            status=PurchaseStatus.COMPLETED,
            token_ids=[str(t.id) for t in tokens],
            completed_at=datetime.utcnow(),
        )
        db.add(purchase)
        await db.commit()
        await db.refresh(purchase)

        logger.info(
            "Dev purchase created: %s → %d tokens (no Stripe)",
            purchase.id,
            len(tokens),
        )
        return purchase
