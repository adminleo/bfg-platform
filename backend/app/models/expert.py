import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Expert(Base):
    """Certified expert/coach/advisor in the network."""
    __tablename__ = "experts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)

    # Profile
    title: Mapped[str] = mapped_column(String(255))
    specializations: Mapped[list] = mapped_column(JSONB, default=list)  # ["leadership", "communication", ...]
    certifications: Mapped[list] = mapped_column(JSONB, default=list)  # ["SCIL Master", "ICF PCC", ...]
    languages: Mapped[list] = mapped_column(JSONB, default=list)  # ["de", "en", ...]
    bio: Mapped[str] = mapped_column(Text)
    years_experience: Mapped[int] = mapped_column(Integer, default=0)

    # Availability
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    calendar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hourly_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Token reselling
    reseller_tier: Mapped[str] = mapped_column(String(50), default="standard")  # standard, premium, partner
    token_discount_pct: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_purchased_ytd: Mapped[int] = mapped_column(Integer, default=0)

    # Platform subscription
    subscription_tier: Mapped[str] = mapped_column(String(50), default="starter")  # starter, professional, enterprise

    # Matching metrics
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    match_success_rate: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sold_tokens: Mapped[list["DiagnosticToken"]] = relationship(back_populates="sold_by_expert", lazy="selectin")
