"""Pydantic schemas for 360° Feedback endpoints."""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


# ── Request schemas ──────────────────────────────────────────

class CreateFeedbackRoundRequest(BaseModel):
    target_user_id: UUID
    title: str = "360° Feedback"
    competencies: list[str] | None = None
    min_raters_per_group: int = 3


class AddRaterRequest(BaseModel):
    email: str
    name: str
    perspective: str  # "self", "supervisor", "peer", "report", "external"


class AddRatersRequest(BaseModel):
    raters: list[AddRaterRequest]


class ConsentRequest(BaseModel):
    access_token: str
    gdpr_consented: bool


class SubmitResponseRequest(BaseModel):
    rater_id: UUID
    competency_scores: dict[str, float]
    scil_scores: dict | None = None
    qualitative_feedback: dict = {}
    conversation: list = []


# ── Response schemas ─────────────────────────────────────────

class RaterResponse(BaseModel):
    id: UUID
    email: str
    name: str
    perspective: str
    status: str
    gdpr_consented: bool
    invited_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class FeedbackRoundResponse(BaseModel):
    id: UUID
    target_user_id: UUID
    title: str
    status: str
    competencies: list[str]
    min_raters_per_group: int
    created_at: datetime
    completed_at: datetime | None = None
    raters: list[RaterResponse] = []

    model_config = {"from_attributes": True}


class FeedbackRoundSummary(BaseModel):
    id: UUID
    title: str
    status: str
    total_raters: int
    completed_raters: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackResultResponse(BaseModel):
    round_id: UUID
    status: str
    aggregated_scores: dict | None = None
    scil_scores_self: dict | None = None
    scil_scores_others: dict | None = None
    johari_window: dict | None = None
    qualitative_summary: str | None = None
    rater_completion: dict[str, dict[str, int]] = {}

    model_config = {"from_attributes": True}


# ── Import schemas ───────────────────────────────────────────

class ImportResultRequest(BaseModel):
    source_tool: str            # "mbti", "disc", "insights", etc.
    source_tool_name: str       # "Myers-Briggs Type Indicator"
    scores: dict                # Tool-specific scores
    original_test_date: datetime | None = None
    provider_name: str | None = None
    notes: str | None = None
    consent_given: bool = False


class ImportResultResponse(BaseModel):
    id: UUID
    source_tool: str
    source_tool_name: str
    scores: dict
    imported_at: datetime
    is_verified: bool

    model_config = {"from_attributes": True}


class AvailableImportTool(BaseModel):
    slug: str
    name: str
    description: str
    score_fields: list[dict[str, str]]  # [{"key": "D", "label": "Dominance", "type": "number"}, ...]
    example: dict
