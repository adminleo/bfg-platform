import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from bfg_core.database import Base


class AIAuditLog(Base):
    """Every LLM call is logged for compliance and cost tracking."""
    __tablename__ = "ai_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Provider info
    provider: Mapped[str] = mapped_column(String(50))  # anthropic, openai, ollama
    model: Mapped[str] = mapped_column(String(100))
    endpoint: Mapped[str] = mapped_column(String(50), default="messages")  # messages, embeddings

    # Request metadata
    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="success")  # success, error, timeout
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Context
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComplianceAuditLog(Base):
    """Immutable audit trail for DSGVO/EU AI Act compliance."""
    __tablename__ = "compliance_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(50))  # consent_given, data_accessed, data_deleted
    user_id: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(100))  # diagnostic_run, feedback_round
    resource_id: Mapped[str] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
