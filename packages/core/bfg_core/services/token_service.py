"""DiagnosticToken lifecycle service — Generate, Activate, Consume.

Manages the full lifecycle of diagnostic tokens:
  EMITTED → SOLD → ASSIGNED → ACTIVATED → CONSUMED
                                              ↘ EXPIRED

Usage:
    from bfg_core.services.token_service import TokenService

    svc = TokenService(session_factory, hmac_secret="...")
    tokens = await svc.generate_token(TokenTier.M, "scil")
    await svc.activate_token(tokens[0].token_code, user_id)
    await svc.consume_token(tokens[0].token_code, run_id)
"""

import logging
import secrets
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker

from bfg_core.models.token import DiagnosticToken, TokenTier, TokenStatus

logger = logging.getLogger(__name__)

# Valid state transitions
_ACTIVATABLE_STATUSES = {TokenStatus.EMITTED, TokenStatus.SOLD, TokenStatus.ASSIGNED}
_CONSUMABLE_STATUSES = {TokenStatus.ACTIVATED}


class TokenService:
    """Async token lifecycle management.

    Uses its own sessions from the factory — does not share the caller's transaction.
    """

    def __init__(self, session_factory: async_sessionmaker, hmac_secret: str):
        self._session_factory = session_factory
        self._hmac_secret = hmac_secret

    async def generate_token(
        self,
        tier: TokenTier,
        diagnostic_type: str,
        *,
        quantity: int = 1,
        sold_by_expert_id: UUID | None = None,
        purchase_price: float | None = None,
        retail_price: float | None = None,
        expires_at: datetime | None = None,
        metadata: dict | None = None,
    ) -> list[DiagnosticToken]:
        """Generate one or more diagnostic tokens with HMAC signatures.

        Returns list of persisted DiagnosticToken objects.
        """
        tokens: list[DiagnosticToken] = []

        async with self._session_factory() as session:
            for _ in range(quantity):
                token_code = secrets.token_urlsafe(32)
                initial_status = TokenStatus.SOLD if sold_by_expert_id else TokenStatus.EMITTED

                # Compute HMAC signature
                token_id_placeholder = ""  # We'll use token_code as the signing input
                signature = DiagnosticToken.generate_signature(
                    token_code, "", diagnostic_type, tier.value, self._hmac_secret,
                )

                token = DiagnosticToken(
                    token_code=token_code,
                    tier=tier,
                    diagnostic_type=diagnostic_type,
                    status=initial_status,
                    sold_by_expert_id=sold_by_expert_id,
                    purchase_price=purchase_price,
                    retail_price=retail_price,
                    expires_at=expires_at,
                    signature=signature,
                    metadata_json=metadata,
                )
                session.add(token)
                tokens.append(token)

            await session.commit()

            # Refresh to get DB-generated fields (id, created_at)
            for token in tokens:
                await session.refresh(token)

        logger.info(
            "Generated %d token(s): tier=%s type=%s",
            len(tokens), tier.value, diagnostic_type,
        )
        return tokens

    async def activate_token(self, token_code: str, user_id: UUID) -> DiagnosticToken:
        """Activate a token by binding it to a user.

        Validates:
        - Token exists
        - Token status is EMITTED, SOLD, or ASSIGNED
        - Token is not expired

        Raises ValueError on invalid state transitions.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(DiagnosticToken).where(DiagnosticToken.token_code == token_code)
            )
            token = result.scalar_one_or_none()

            if not token:
                raise ValueError(f"Token not found: {token_code[:8]}...")

            if token.status not in _ACTIVATABLE_STATUSES:
                raise ValueError(
                    f"Token cannot be activated: current status is {token.status.value}"
                )

            if token.expires_at and token.expires_at < datetime.utcnow():
                token.status = TokenStatus.EXPIRED
                await session.commit()
                raise ValueError("Token has expired")

            token.user_id = user_id
            token.status = TokenStatus.ACTIVATED
            token.activated_at = datetime.utcnow()

            # Re-compute signature with the new user binding
            token.signature = DiagnosticToken.generate_signature(
                token.token_code, str(user_id), token.diagnostic_type,
                token.tier.value, self._hmac_secret,
            )

            await session.commit()
            await session.refresh(token)

        logger.info("Token activated: %s → user %s", token_code[:8], user_id)
        return token

    async def consume_token(self, token_code: str, run_id: UUID) -> DiagnosticToken:
        """Consume a token by binding it to a diagnostic run.

        Validates:
        - Token exists and status is ACTIVATED
        - HMAC signature is valid (tamper detection)

        Raises ValueError on invalid state or signature failure.
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(DiagnosticToken).where(DiagnosticToken.token_code == token_code)
            )
            token = result.scalar_one_or_none()

            if not token:
                raise ValueError(f"Token not found: {token_code[:8]}...")

            if token.status not in _CONSUMABLE_STATUSES:
                raise ValueError(
                    f"Token cannot be consumed: current status is {token.status.value}"
                )

            # Verify signature integrity
            if not token.verify_signature(self._hmac_secret):
                logger.error("Token signature verification failed: %s", token_code[:8])
                raise ValueError("Token signature verification failed — possible tampering")

            token.run_id = run_id
            token.status = TokenStatus.CONSUMED
            token.consumed_at = datetime.utcnow()

            await session.commit()
            await session.refresh(token)

        logger.info("Token consumed: %s → run %s", token_code[:8], run_id)
        return token

    async def validate_token(self, token_code: str) -> tuple[bool, str]:
        """Validate a token for use.

        Returns:
            (is_valid, reason_if_invalid)
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(DiagnosticToken).where(DiagnosticToken.token_code == token_code)
            )
            token = result.scalar_one_or_none()

            if not token:
                return False, "Token not found"

            if token.status == TokenStatus.CONSUMED:
                return False, "Token has already been consumed"

            if token.status == TokenStatus.EXPIRED:
                return False, "Token has expired"

            if token.expires_at and token.expires_at < datetime.utcnow():
                return False, "Token has expired"

            if token.status == TokenStatus.ACTIVATED:
                if not token.verify_signature(self._hmac_secret):
                    return False, "Token signature verification failed"
                return True, "Token is valid and ready to use"

            if token.status in _ACTIVATABLE_STATUSES:
                return True, "Token is valid but needs activation"

            return False, f"Unexpected token status: {token.status.value}"

    async def get_user_tokens(
        self,
        user_id: UUID,
        *,
        status: TokenStatus | None = None,
    ) -> list[DiagnosticToken]:
        """Get all tokens for a user, optionally filtered by status."""
        async with self._session_factory() as session:
            stmt = select(DiagnosticToken).where(DiagnosticToken.user_id == user_id)
            if status:
                stmt = stmt.where(DiagnosticToken.status == status)
            stmt = stmt.order_by(DiagnosticToken.created_at.desc())

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def expire_tokens(self) -> int:
        """Batch-expire all tokens past their expiration date.

        Called by Celery beat schedule (daily).
        Returns the number of tokens expired.
        """
        async with self._session_factory() as session:
            now = datetime.utcnow()
            stmt = (
                update(DiagnosticToken)
                .where(
                    DiagnosticToken.expires_at < now,
                    DiagnosticToken.status.in_([
                        TokenStatus.EMITTED,
                        TokenStatus.SOLD,
                        TokenStatus.ASSIGNED,
                        TokenStatus.ACTIVATED,
                    ]),
                )
                .values(status=TokenStatus.EXPIRED)
            )
            result = await session.execute(stmt)
            await session.commit()

            count = result.rowcount
            if count > 0:
                logger.info("Expired %d token(s)", count)
            return count
