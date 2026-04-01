import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.token import DiagnosticToken, TokenTier, TokenStatus
from app.schemas.token import TokenEmitRequest, TokenAssignRequest, TokenActivateRequest, TokenResponse, TokenBatchResponse

router = APIRouter(prefix="/tokens", tags=["tokens"])


@router.post("/emit", response_model=TokenBatchResponse, status_code=status.HTTP_201_CREATED)
async def emit_tokens(data: TokenEmitRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """System owner emits new one-time-usage tokens."""
    tokens = []
    for _ in range(data.quantity):
        token_id = uuid.uuid4()
        token_code = secrets.token_urlsafe(32)

        signature = DiagnosticToken.generate_signature(
            str(token_id), "", data.diagnostic_type, data.tier.value, settings.token_hmac_secret
        )

        token = DiagnosticToken(
            id=token_id,
            token_code=token_code,
            tier=data.tier,
            diagnostic_type=data.diagnostic_type,
            status=TokenStatus.EMITTED,
            signature=signature,
            expires_at=datetime.utcnow() + timedelta(days=365),
        )

        if data.expert_id:
            token.sold_by_expert_id = data.expert_id
            token.status = TokenStatus.SOLD

        db.add(token)
        tokens.append(token)

    await db.commit()
    for t in tokens:
        await db.refresh(t)

    return TokenBatchResponse(tokens=tokens, count=len(tokens))


@router.post("/assign", response_model=TokenResponse)
async def assign_token(data: TokenAssignRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Assign a token to a specific user (UID-binding)."""
    result = await db.execute(
        select(DiagnosticToken).where(DiagnosticToken.token_code == data.token_code)
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    if token.status not in (TokenStatus.EMITTED, TokenStatus.SOLD):
        raise HTTPException(status_code=400, detail=f"Token cannot be assigned (status: {token.status})")

    token.user_id = data.user_id
    token.status = TokenStatus.ASSIGNED

    # Re-sign with user binding
    token.signature = DiagnosticToken.generate_signature(
        str(token.id), str(data.user_id), token.diagnostic_type, token.tier.value, settings.token_hmac_secret
    )

    await db.commit()
    await db.refresh(token)
    return token


@router.post("/activate", response_model=TokenResponse)
async def activate_token(data: TokenActivateRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Activate a token on link click — starts the diagnostic."""
    result = await db.execute(
        select(DiagnosticToken).where(DiagnosticToken.token_code == data.token_code)
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    if token.status != TokenStatus.ASSIGNED:
        raise HTTPException(status_code=400, detail=f"Token must be assigned before activation (status: {token.status})")
    if token.expires_at and token.expires_at < datetime.utcnow():
        token.status = TokenStatus.EXPIRED
        await db.commit()
        raise HTTPException(status_code=400, detail="Token has expired")

    token.status = TokenStatus.ACTIVATED
    token.activated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(token)
    return token


@router.get("/{token_code}", response_model=TokenResponse)
async def get_token(token_code: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Get token details by code."""
    result = await db.execute(
        select(DiagnosticToken).where(DiagnosticToken.token_code == token_code)
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token
