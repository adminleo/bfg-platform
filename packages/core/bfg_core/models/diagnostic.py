import uuid
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bfg_core.database import Base


class DiagnosticCategory(str, enum.Enum):
    PERSONALITY = "personality"
    COMMUNICATION = "communication"
    VALUES = "values"
    STRENGTHS = "strengths"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    RESILIENCE = "resilience"
    LEADERSHIP = "leadership"
    TEAM = "team"
    MOTIVATION = "motivation"
    COGNITION = "cognition"


class Diagnostic(Base):
    """Available diagnostic instruments on the platform."""
    __tablename__ = "diagnostics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[DiagnosticCategory] = mapped_column(SAEnum(DiagnosticCategory))
    scientific_basis: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Configuration
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    min_questions: Mapped[int] = mapped_column(Integer, default=24)
    max_questions: Mapped[int] = mapped_column(Integer, default=100)

    # Tiers available
    available_tiers: Mapped[list] = mapped_column(JSONB, default=lambda: ["S", "M", "L", "XL"])

    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    runs: Mapped[list["DiagnosticRun"]] = relationship(back_populates="diagnostic", lazy="selectin")


class DiagnosticRun(Base):
    """A single execution of a diagnostic for a user."""
    __tablename__ = "diagnostic_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    diagnostic_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("diagnostics.id"))
    token_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("diagnostic_tokens.id"), nullable=True)
    tier: Mapped[str] = mapped_column(String(5))

    # State
    status: Mapped[str] = mapped_column(String(30), default="started")
    progress: Mapped[float] = mapped_column(Float, default=0.0)

    # Conversation history
    conversation: Mapped[list] = mapped_column(JSONB, default=list)
    answers: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Per-item response data (for psychometrics / IRT)
    # Format: [{"item_id": "S01", "score": 3.2, "confidence": 0.8,
    #           "reasoning": "...", "scored_at": "...", "turn_number": 5}]
    item_responses: Mapped[list] = mapped_column(JSONB, default=list)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="diagnostic_runs")
    diagnostic: Mapped["Diagnostic"] = relationship(back_populates="runs")
    result: Mapped["DiagnosticResult | None"] = relationship(back_populates="run", uselist=False)


class DiagnosticResult(Base):
    """Computed result of a diagnostic run."""
    __tablename__ = "diagnostic_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("diagnostic_runs.id"), unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Scores
    scores: Mapped[dict] = mapped_column(JSONB)
    summary: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[list] = mapped_column(JSONB, default=list)

    # Visualization data (e.g., SCIL polygon)
    polygon_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Metadata
    norm_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    percentiles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    run: Mapped["DiagnosticRun"] = relationship(back_populates="result")
