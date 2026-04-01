from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.expert import Expert

router = APIRouter(prefix="/experts", tags=["experts"])


@router.get("/")
async def list_experts(
    specialization: str | None = None,
    language: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List available experts, optionally filtered."""
    query = select(Expert).where(Expert.is_available == True)
    result = await db.execute(query)
    experts = result.scalars().all()

    # Filter in Python for JSONB fields (could be optimized with DB-level filtering)
    if specialization:
        experts = [e for e in experts if specialization in e.specializations]
    if language:
        experts = [e for e in experts if language in e.languages]

    return experts


@router.get("/{expert_id}")
async def get_expert(expert_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get expert profile details."""
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert
