"""Code purchase model — Tracks Stripe checkout sessions and generated codes.

Lifecycle:
    User selects package → PENDING (Stripe Checkout created)
    Stripe webhook confirms payment → COMPLETED (tokens generated)
    Error during fulfillment → FAILED
    Refund processed → REFUNDED
"""

import uuid
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


class PurchaseStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class CodePackageType(str, enum.Enum):
    SINGLE = "single"
    PACK_10 = "pack_10"
    PACK_25 = "pack_25"
    PACK_50 = "pack_50"
    PACK_100 = "pack_100"


class CodePurchase(Base):
    """Records a code purchase transaction linked to Stripe."""

    __tablename__ = "code_purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    # Stripe references
    stripe_session_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # Package details
    package_type: Mapped[CodePackageType] = mapped_column(SAEnum(CodePackageType))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents: Mapped[int] = mapped_column(Integer)
    total_price_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="eur")

    # Status
    status: Mapped[PurchaseStatus] = mapped_column(
        SAEnum(PurchaseStatus), default=PurchaseStatus.PENDING
    )

    # Generated tokens (list of UUID strings)
    token_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    buyer: Mapped["User"] = relationship()  # noqa: F821
