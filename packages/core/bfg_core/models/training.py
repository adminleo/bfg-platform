"""Training models — Daily micro-training personalized from SCIL results.

Models:
    LearningContent  — Reusable training modules (video, exercise, reflection, article)
    TrainingPlan     — Personalized multi-week plan for a user
    TrainingDay      — Single day within a plan (links to content)
    TrainingProgress — User's progress tracking per day
"""

import uuid
import enum
from datetime import datetime, date

from sqlalchemy import (
    String, DateTime, Date, Float, Integer, Text, Boolean,
    ForeignKey, Enum as SAEnum, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ContentType(str, enum.Enum):
    VIDEO = "video"
    EXERCISE = "exercise"
    REFLECTION = "reflection"
    ARTICLE = "article"
    QUIZ = "quiz"


class ContentArea(str, enum.Enum):
    """Maps to SCIL areas."""
    SENSUS = "sensus"
    CORPUS = "corpus"
    INTELLEKTUS = "intellektus"
    LINGUA = "lingua"
    GENERAL = "general"


class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DayStatus(str, enum.Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ---------------------------------------------------------------------------
# LearningContent — Reusable training modules
# ---------------------------------------------------------------------------

class LearningContent(Base):
    """A reusable piece of learning content (video, exercise, article, etc.)."""

    __tablename__ = "learning_contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    content_type: Mapped[ContentType] = mapped_column(SAEnum(ContentType))
    area: Mapped[ContentArea] = mapped_column(SAEnum(ContentArea))

    # Which SCIL frequency this targets (e.g., "S01", "C03", "I02", "L04")
    target_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Difficulty: 1 (beginner) to 5 (advanced)
    difficulty: Mapped[int] = mapped_column(Integer, default=2)

    # Estimated duration in minutes
    duration_minutes: Mapped[int] = mapped_column(Integer, default=10)

    # Content body (Markdown for articles, structured JSON for exercises)
    body: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Optional video URL
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Tags for filtering
    tags: Mapped[list] = mapped_column(JSONB, default=list)

    # Author information
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Premium flag — content that requires purchase
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ordering within a content sequence
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Lecture / lesson structure (for multi-part trainings)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_contents.id"), nullable=True
    )
    lesson_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Self-referential relationship for lessons within a training
    lessons: Mapped[list["LearningContent"]] = relationship(
        "LearningContent",
        foreign_keys="LearningContent.parent_id",
        order_by="LearningContent.lesson_number",
        lazy="selectin",
    )


# ---------------------------------------------------------------------------
# TrainingPlan — Personalized multi-week plan
# ---------------------------------------------------------------------------

class TrainingPlan(Base):
    """A personalized training plan generated from SCIL diagnostic results."""

    __tablename__ = "training_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    # Link to the diagnostic result that generated this plan
    result_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("diagnostic_results.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Plan configuration
    total_weeks: Mapped[int] = mapped_column(Integer, default=4)
    days_per_week: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[PlanStatus] = mapped_column(
        SAEnum(PlanStatus), default=PlanStatus.DRAFT
    )

    # AI-generated focus areas based on SCIL results
    # e.g., {"primary": "sensus", "secondary": "lingua", "strengths": ["corpus"]}
    focus_areas: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Overall plan metadata from AI
    ai_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Progress tracking
    current_week: Mapped[int] = mapped_column(Integer, default=1)
    current_day: Mapped[int] = mapped_column(Integer, default=1)
    overall_progress: Mapped[float] = mapped_column(Float, default=0.0)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    days: Mapped[list["TrainingDay"]] = relationship(
        back_populates="plan", lazy="selectin",
        order_by="TrainingDay.week_number, TrainingDay.day_number",
    )


# ---------------------------------------------------------------------------
# TrainingDay — Single day within a plan
# ---------------------------------------------------------------------------

class TrainingDay(Base):
    """A single training day within a plan, linking to specific content."""

    __tablename__ = "training_days"
    __table_args__ = (
        UniqueConstraint("plan_id", "week_number", "day_number", name="uq_plan_week_day"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_plans.id", ondelete="CASCADE")
    )
    content_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_contents.id"), nullable=True
    )

    week_number: Mapped[int] = mapped_column(Integer)
    day_number: Mapped[int] = mapped_column(Integer)

    # Day-specific title and coaching note from AI
    title: Mapped[str] = mapped_column(String(255))
    coaching_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Target area for this day
    area: Mapped[ContentArea] = mapped_column(SAEnum(ContentArea))

    status: Mapped[DayStatus] = mapped_column(
        SAEnum(DayStatus), default=DayStatus.LOCKED
    )

    # Scheduled date (optional, for calendar integration)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    plan: Mapped["TrainingPlan"] = relationship(back_populates="days")
    content: Mapped["LearningContent | None"] = relationship(lazy="selectin")
    progress: Mapped["TrainingProgress | None"] = relationship(
        back_populates="day", uselist=False, lazy="selectin"
    )


# ---------------------------------------------------------------------------
# TrainingProgress — User completion tracking
# ---------------------------------------------------------------------------

class TrainingProgress(Base):
    """Tracks a user's progress on a single training day."""

    __tablename__ = "training_progress"
    __table_args__ = (
        UniqueConstraint("day_id", "user_id", name="uq_day_user_progress"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    day_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("training_days.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    # Completion
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # User reflection / notes
    reflection: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Self-rating: 1-5 how useful was this?
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Exercise answers (for quiz/exercise content types)
    answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # AI feedback on the reflection
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    day: Mapped["TrainingDay"] = relationship(back_populates="progress")
    user: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821


# ---------------------------------------------------------------------------
# TrainingEnrollment — User enrollment in a training content
# ---------------------------------------------------------------------------

class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TrainingEnrollment(Base):
    """Tracks a user's enrollment in a specific learning content."""

    __tablename__ = "training_enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_user_content_enrollment"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_contents.id")
    )

    status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE
    )

    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # For premium content: link to a purchase that unlocked it
    purchase_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821
    content: Mapped["LearningContent"] = relationship(lazy="selectin")
