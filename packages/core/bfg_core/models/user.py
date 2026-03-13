import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="trainee")  # trainee, coach, expert, admin, provider
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tokens: Mapped[list["DiagnosticToken"]] = relationship(back_populates="user", lazy="selectin")
    diagnostic_runs: Mapped[list["DiagnosticRun"]] = relationship(back_populates="user", lazy="selectin")

    # Coach relationships
    coaching: Mapped[list["CoachAssignment"]] = relationship(  # noqa: F821
        foreign_keys="CoachAssignment.coach_id", lazy="selectin",
        overlaps="coach",
    )
    coached_by: Mapped[list["CoachAssignment"]] = relationship(  # noqa: F821
        foreign_keys="CoachAssignment.coachee_id", lazy="selectin",
        overlaps="coachee",
    )
