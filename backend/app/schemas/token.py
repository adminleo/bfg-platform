from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.token import TokenTier, TokenStatus


class TokenEmitRequest(BaseModel):
    tier: TokenTier
    diagnostic_type: str
    quantity: int = 1
    expert_id: UUID | None = None


class TokenAssignRequest(BaseModel):
    token_code: str
    user_id: UUID


class TokenActivateRequest(BaseModel):
    token_code: str


class TokenResponse(BaseModel):
    id: UUID
    token_code: str
    tier: TokenTier
    diagnostic_type: str
    status: TokenStatus
    user_id: UUID | None
    run_id: UUID | None
    expires_at: datetime | None
    activated_at: datetime | None
    consumed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenBatchResponse(BaseModel):
    tokens: list[TokenResponse]
    count: int
