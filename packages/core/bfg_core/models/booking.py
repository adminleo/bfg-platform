"""Booking models — Coach availability slots, coachee bookings, and AI briefings.

Models:
    AvailabilitySlot  — Coach's available time windows
    Booking           — A coachee's reserved session with a coach
    SessionBriefing   — AI-generated session preparation brief for coach
"""

import uuid
import enum
from datetime import datetime, time

from sqlalchemy import (
    String, DateTime, Date, Time, Float, Integer, Text, Boolean,
    ForeignKey, Enum as SAEnum, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SlotRecurrence(str, enum.Enum):
    ONCE = "once"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"


class BookingStatus(str, enum.Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class BriefingStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# AvailabilitySlot — Coach's available time windows
# ---------------------------------------------------------------------------

class AvailabilitySlot(Base):
    """A time slot when a coach is available for sessions."""

    __tablename__ = "availability_slots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    # Day of week (0=Monday, 6=Sunday)
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    # Duration per session in minutes (default 60)
    session_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Recurrence
    recurrence: Mapped[SlotRecurrence] = mapped_column(
        SAEnum(SlotRecurrence), default=SlotRecurrence.WEEKLY
    )

    # Optional specific date (for ONCE slots)
    specific_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Active flag
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    coach: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821


# ---------------------------------------------------------------------------
# Booking — Coachee's reserved session
# ---------------------------------------------------------------------------

class Booking(Base):
    """A booked coaching session between a coach and coachee."""

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    coach_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    coachee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    slot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("availability_slots.id"), nullable=True
    )

    # Session time
    scheduled_at: Mapped[datetime] = mapped_column(DateTime)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Status
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus), default=BookingStatus.REQUESTED
    )

    # Session details
    topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coachee_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    coach_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Video/meeting link
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Post-session
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    coach: Mapped["User"] = relationship(foreign_keys=[coach_id], lazy="selectin")  # noqa: F821
    coachee: Mapped["User"] = relationship(foreign_keys=[coachee_id], lazy="selectin")  # noqa: F821
    slot: Mapped["AvailabilitySlot | None"] = relationship(lazy="selectin")
    briefing: Mapped["SessionBriefing | None"] = relationship(
        back_populates="booking", uselist=False, lazy="selectin"
    )


# ---------------------------------------------------------------------------
# SessionBriefing — AI-generated session prep for coach
# ---------------------------------------------------------------------------

class SessionBriefing(Base):
    """AI-generated briefing document to help a coach prepare for a session."""

    __tablename__ = "session_briefings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bookings.id"), unique=True
    )

    # Status
    status: Mapped[BriefingStatus] = mapped_column(
        SAEnum(BriefingStatus), default=BriefingStatus.PENDING
    )

    # Briefing content (Markdown)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Structured data
    coachee_profile_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    scil_highlights: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    suggested_topics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    suggested_exercises: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    previous_session_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    training_progress_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    booking: Mapped["Booking"] = relationship(back_populates="briefing")
