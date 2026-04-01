"""Coach-Coachee assignment model — Links coaches to coachees with diagnostic codes.

Lifecycle:
    Coach invites coachee → INVITED (email sent)
    Coachee registers → PENDING (code not yet redeemed)
    Coachee redeems code → ACTIVE (in diagnostik/training)
    Diagnostik complete → COMPLETED
    Coach archives → ARCHIVED
"""

import uuid
import enum
import secrets
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


class AssignmentStatus(str, enum.Enum):
    INVITED = "invited"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CoachAssignment(Base):
    """Links a coach to a coachee with a diagnostic code."""

    __tablename__ = "coach_assignments"
    __table_args__ = (
        UniqueConstraint("coach_id", "coachee_email", name="uq_coach_coachee_email"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    coachee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Invitation details
    coachee_email: Mapped[str] = mapped_column(String(255))
    invitation_token: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True
    )

    # Associated diagnostic code
    token_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("diagnostic_tokens.id"), nullable=True
    )

    # Status
    status: Mapped[AssignmentStatus] = mapped_column(
        SAEnum(AssignmentStatus), default=AssignmentStatus.INVITED
    )

    # Coach notes
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    coach: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[coach_id], overlaps="coaching", lazy="selectin",
    )
    coachee: Mapped["User | None"] = relationship(  # noqa: F821
        foreign_keys=[coachee_id], overlaps="coached_by", lazy="selectin",
    )
    token: Mapped["DiagnosticToken | None"] = relationship(lazy="selectin")  # noqa: F821

    @staticmethod
    def generate_invitation_token() -> str:
        """Generate a secure invitation token."""
        return secrets.token_urlsafe(48)
