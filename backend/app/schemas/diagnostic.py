from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DiagnosticListItem(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str
    category: str
    available_tiers: list[str]
    is_active: bool

    model_config = {"from_attributes": True}


class StartDiagnosticRequest(BaseModel):
    token_code: str


class ChatMessage(BaseModel):
    role: str  # "user" or "agent"
    content: str


class DiagnosticRunResponse(BaseModel):
    id: UUID
    diagnostic_slug: str
    tier: str
    status: str
    progress: float
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class DiagnosticResultResponse(BaseModel):
    id: UUID
    run_id: UUID
    scores: dict
    summary: str
    recommendations: list
    polygon_data: dict | None
    percentiles: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SCILPolygonData(BaseModel):
    """SCIL-specific polygon visualization data."""
    sensus: dict[str, float]  # {"inner_presence": 7.2, "conviction": 6.8, ...}
    corpus: dict[str, float]
    intellektus: dict[str, float]
    lingua: dict[str, float]
    overall_balance: float  # 0-10 how balanced the polygon is
