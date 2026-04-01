import uuid
import hmac
import hashlib
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


class TokenTier(str, enum.Enum):
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class TokenStatus(str, enum.Enum):
    EMITTED = "emitted"
    SOLD = "sold"
    ASSIGNED = "assigned"
    ACTIVATED = "activated"
    CONSUMED = "consumed"
    EXPIRED = "expired"


class DiagnosticToken(Base):
    __tablename__ = "diagnostic_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tier: Mapped[TokenTier] = mapped_column(SAEnum(TokenTier))
    diagnostic_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[TokenStatus] = mapped_column(SAEnum(TokenStatus), default=TokenStatus.EMITTED)

    # Binding
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Reseller tracking
    sold_by_expert_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    purchase_price: Mapped[float | None] = mapped_column(nullable=True)
    retail_price: Mapped[float | None] = mapped_column(nullable=True)

    # Signature for integrity
    signature: Mapped[str] = mapped_column(String(128))

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="tokens")

    @staticmethod
    def generate_signature(token_id: str, user_id: str, diagnostic_type: str, tier: str, secret: str) -> str:
        message = f"{token_id}:{user_id}:{diagnostic_type}:{tier}"
        return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

    def verify_signature(self, secret: str) -> bool:
        expected = self.generate_signature(
            str(self.id), str(self.user_id or ""), self.diagnostic_type, self.tier.value, secret
        )
        return hmac.compare_digest(self.signature, expected)
