"""
360° Feedback Models — Multi-Rater Feedback System

Tables:
  - feedback_rounds: A complete 360° feedback cycle for one target user
  - feedback_raters: Individual raters invited to a round
  - feedback_responses: Completed feedback with scores and qualitative data
"""

import uuid
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer, Text, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FeedbackRoundStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"               # Invitations sent, collecting feedback
    ANALYSIS = "analysis"           # All raters done, computing results
    COMPLETED = "completed"         # Results available
    CANCELLED = "cancelled"


class RaterPerspective(str, enum.Enum):
    SELF = "self"
    SUPERVISOR = "supervisor"
    PEER = "peer"
    REPORT = "report"              # Direct report (Unterstellte)
    EXTERNAL = "external"          # Customer, partner, etc.


class RaterStatus(str, enum.Enum):
    INVITED = "invited"
    STARTED = "started"
    COMPLETED = "completed"
    DECLINED = "declined"
    EXPIRED = "expired"


class FeedbackRound(Base):
    """A complete 360° feedback cycle for one target user."""
    __tablename__ = "feedback_rounds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Round metadata
    title: Mapped[str] = mapped_column(String(255), default="360° Feedback")
    status: Mapped[FeedbackRoundStatus] = mapped_column(
        SAEnum(FeedbackRoundStatus), default=FeedbackRoundStatus.DRAFT
    )

    # Configuration
    competencies: Mapped[list] = mapped_column(
        JSONB,
        default=lambda: [
            "persuasion", "analytical_thinking", "empathy", "presence",
            "strategic_thinking", "storytelling", "team_leadership", "clarity",
        ],
    )
    min_raters_per_group: Mapped[int] = mapped_column(Integer, default=3)
    anonymity_threshold: Mapped[int] = mapped_column(Integer, default=3)

    # DSGVO Compliance
    gdpr_consent_text: Mapped[str] = mapped_column(
        Text,
        default=(
            "Ich willige ein, dass meine Antworten anonymisiert verarbeitet werden. "
            "Die Daten werden ausschließlich zur Erstellung des 360°-Feedback-Reports genutzt "
            "und nach 24 Monaten automatisch gelöscht (Art. 6 Abs. 1 lit. a DSGVO, Art. 9 DSGVO). "
            "Ich kann meine Einwilligung jederzeit widerrufen."
        ),
    )
    data_retention_months: Mapped[int] = mapped_column(Integer, default=24)

    # Results
    aggregated_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    scil_scores_self: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    scil_scores_others: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    johari_window: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    qualitative_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deletion_scheduled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    raters: Mapped[list["FeedbackRater"]] = relationship(
        back_populates="round", lazy="selectin", cascade="all, delete-orphan"
    )


class FeedbackRater(Base):
    """An individual rater in a 360° feedback round."""
    __tablename__ = "feedback_raters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("feedback_rounds.id"))

    # Rater identity
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    perspective: Mapped[RaterPerspective] = mapped_column(SAEnum(RaterPerspective))
    status: Mapped[RaterStatus] = mapped_column(SAEnum(RaterStatus), default=RaterStatus.INVITED)

    # Access
    access_token: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    gdpr_consented: Mapped[bool] = mapped_column(Boolean, default=False)
    gdpr_consented_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    invited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    round: Mapped["FeedbackRound"] = relationship(back_populates="raters")
    response: Mapped["FeedbackResponse | None"] = relationship(
        back_populates="rater", uselist=False, cascade="all, delete-orphan"
    )


class FeedbackResponse(Base):
    """Completed feedback response with scores and qualitative data."""
    __tablename__ = "feedback_responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rater_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feedback_raters.id"), unique=True
    )
    round_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("feedback_rounds.id"))

    # Competency scores (1-10 per competency)
    competency_scores: Mapped[dict] = mapped_column(JSONB, default=dict)
    # e.g. {"persuasion": 7.5, "empathy": 8.0, ...}

    # SCIL-mapped scores (computed from competency scores)
    scil_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # e.g. {"sensus": {"conviction": 7.2, ...}, ...}

    # Qualitative feedback
    qualitative_feedback: Mapped[dict] = mapped_column(JSONB, default=dict)
    # e.g. {"strengths": "...", "development_areas": "...", "key_themes": [...]}

    # Conversation history (agent-led conversation)
    conversation: Mapped[list] = mapped_column(JSONB, default=list)

    # De-identification log (what was removed from free text)
    deidentification_log: Mapped[list] = mapped_column(JSONB, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    rater: Mapped["FeedbackRater"] = relationship(back_populates="response")


class ImportedResult(Base):
    """Imported result from a proprietary third-party diagnostic."""
    __tablename__ = "imported_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Source
    source_tool: Mapped[str] = mapped_column(String(100))  # "mbti", "disc", "insights", etc.
    source_tool_name: Mapped[str] = mapped_column(String(255))  # Display name
    import_type: Mapped[str] = mapped_column(String(50), default="manual")  # manual, csv, api

    # Scores (generic — we only store numeric scores, never items or report texts)
    scores: Mapped[dict] = mapped_column(JSONB)
    # e.g. MBTI: {"type": "INTJ", "E_I": -3.2, "S_N": 2.8, ...}
    # e.g. DISC: {"D": 78, "I": 45, "S": 32, "C": 65}

    # Metadata (date of original test, provider, etc.)
    original_test_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User consent
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_text: Mapped[str] = mapped_column(
        Text,
        default=(
            "Ich bestätige, dass ich berechtigt bin, diese Ergebnisse hochzuladen, "
            "und willige in die Verarbeitung auf dieser Plattform ein (Art. 6 Abs. 1 lit. a DSGVO)."
        ),
    )

    # Timestamps
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Validity
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
