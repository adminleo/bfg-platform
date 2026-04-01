from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.diagnostic import Diagnostic, DiagnosticRun, DiagnosticResult
from app.models.token import DiagnosticToken, TokenStatus
from app.schemas.diagnostic import DiagnosticListItem, StartDiagnosticRequest, DiagnosticRunResponse, DiagnosticResultResponse

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/", response_model=list[DiagnosticListItem])
async def list_diagnostics(db: AsyncSession = Depends(get_db)):
    """List all available diagnostic instruments."""
    result = await db.execute(select(Diagnostic).where(Diagnostic.is_active == True))
    return result.scalars().all()


@router.get("/{slug}")
async def get_diagnostic(slug: str, db: AsyncSession = Depends(get_db)):
    """Get details of a specific diagnostic."""
    result = await db.execute(select(Diagnostic).where(Diagnostic.slug == slug))
    diagnostic = result.scalar_one_or_none()
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    return diagnostic


@router.post("/start", response_model=DiagnosticRunResponse)
async def start_diagnostic(data: StartDiagnosticRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Start a diagnostic run using an activated token."""
    # Find and validate token
    token_result = await db.execute(
        select(DiagnosticToken).where(DiagnosticToken.token_code == data.token_code)
    )
    token = token_result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    if token.status != TokenStatus.ACTIVATED:
        raise HTTPException(status_code=400, detail="Token must be activated first")
    if not token.user_id:
        raise HTTPException(status_code=400, detail="Token is not assigned to a user")

    # Find the diagnostic
    diag_result = await db.execute(
        select(Diagnostic).where(Diagnostic.slug == token.diagnostic_type)
    )
    diagnostic = diag_result.scalar_one_or_none()
    if not diagnostic:
        raise HTTPException(status_code=404, detail=f"Diagnostic '{token.diagnostic_type}' not found")

    # Create the run
    run = DiagnosticRun(
        user_id=token.user_id,
        diagnostic_id=diagnostic.id,
        token_id=token.id,
        tier=token.tier.value,
    )
    db.add(run)

    # Link token to run
    token.run_id = run.id
    token.status = TokenStatus.CONSUMED

    await db.commit()
    await db.refresh(run)

    return DiagnosticRunResponse(
        id=run.id,
        diagnostic_slug=diagnostic.slug,
        tier=run.tier,
        status=run.status,
        progress=run.progress,
        started_at=run.started_at,
        completed_at=run.completed_at,
    )


@router.get("/runs/{run_id}", response_model=DiagnosticRunResponse)
async def get_run(run_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Get status of a diagnostic run."""
    result = await db.execute(select(DiagnosticRun).where(DiagnosticRun.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    diag_result = await db.execute(select(Diagnostic).where(Diagnostic.id == run.diagnostic_id))
    diagnostic = diag_result.scalar_one_or_none()

    return DiagnosticRunResponse(
        id=run.id,
        diagnostic_slug=diagnostic.slug if diagnostic else "unknown",
        tier=run.tier,
        status=run.status,
        progress=run.progress,
        started_at=run.started_at,
        completed_at=run.completed_at,
    )


@router.get("/results/{run_id}", response_model=DiagnosticResultResponse)
async def get_result(run_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Get the result of a completed diagnostic run."""
    result = await db.execute(
        select(DiagnosticResult).where(DiagnosticResult.run_id == run_id)
    )
    diagnostic_result = result.scalar_one_or_none()
    if not diagnostic_result:
        raise HTTPException(status_code=404, detail="Result not found")
    return diagnostic_result
