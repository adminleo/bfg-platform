"""SCIL API routes — session management and SSE streaming for diagnostics.

Endpoints:
    POST   /scil/sessions              - Start new SCIL diagnostic session
    GET    /scil/sessions               - List all sessions for current user
    GET    /scil/sessions/{id}          - Get session details
    POST   /scil/sessions/{id}/message  - Send message to agent
    GET    /scil/sessions/{id}/stream   - SSE stream for live events
    PATCH  /scil/sessions/{id}          - Rename session
    DELETE /scil/sessions/{id}          - Soft-delete session
    GET    /scil/sessions/{id}/result   - Get final assessment result
"""

import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.models.user import User
from bfg_core.models.diagnostic import Diagnostic, DiagnosticRun, DiagnosticResult
from bfg_core.models.token import TokenStatus
from bfg_core.services.token_service import TokenService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class SessionCreate(BaseModel):
    title: str | None = None


class SessionMessage(BaseModel):
    content: str


class SessionUpdate(BaseModel):
    title: str | None = None


class SessionResponse(BaseModel):
    id: str
    title: str | None
    status: str
    progress: float
    created_at: str
    completed_at: str | None = None

    model_config = {"from_attributes": True}


class SessionDetailResponse(BaseModel):
    id: str
    title: str | None
    status: str
    progress: float
    conversation: list[dict]
    scores: dict | None = None
    polygon: dict | None = None
    cluster_progress: dict | None = None
    items_scored: int = 0
    items_total: int = 100
    suggestions: list[str] | None = None
    created_at: str
    completed_at: str | None = None


class MessageResponse(BaseModel):
    events: list[dict]


class ResultResponse(BaseModel):
    id: str
    scores: dict
    summary: str
    recommendations: list[dict]
    polygon_data: dict | None = None
    created_at: str


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_scil_routes(
    get_db,
    get_current_user,
    get_agent,
    token_service=None,
):
    """Factory to create SCIL routes with injected dependencies.

    Args:
        get_db: FastAPI dependency for DB session
        get_current_user: FastAPI dependency for authenticated user
        get_agent: callable that returns the DiagnosisAgent instance
        token_service: callable returning TokenService or None (lazy init)
    """
    router = APIRouter(prefix="/scil", tags=["scil"])

    @router.post("/sessions", response_model=SessionResponse)
    async def create_session(
        body: SessionCreate | None = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Start a new SCIL diagnostic session."""
        # Find the SCIL diagnostic
        result = await db.execute(
            select(Diagnostic).where(Diagnostic.slug == "scil")
        )
        diagnostic = result.scalar_one_or_none()
        if not diagnostic:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SCIL diagnostic not found. Seed data missing.",
            )

        # Token guard: require a valid activated code
        consumed_token = None
        _token_svc = token_service() if callable(token_service) else token_service
        if _token_svc:
            user_tokens = await _token_svc.get_user_tokens(
                user.id, status=TokenStatus.ACTIVATED
            )
            scil_tokens = [t for t in user_tokens if t.diagnostic_type == "scil"]
            if not scil_tokens:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Kein gueltiger Diagnostik-Code vorhanden. Bitte Code einloesen oder kaufen.",
                )
            consumed_token = scil_tokens[0]

            # 1:1 code-to-session: check if this token already has an active run
            if consumed_token:
                existing_run_result = await db.execute(
                    select(DiagnosticRun).where(
                        DiagnosticRun.token_id == consumed_token.id,
                        DiagnosticRun.status.notin_(["deleted"]),
                    )
                )
                existing_run = existing_run_result.scalar_one_or_none()
                if existing_run:
                    # Return existing session instead of creating duplicate
                    logger.info(
                        "Token %s already bound to run %s — returning existing session",
                        str(consumed_token.id)[:8],
                        str(existing_run.id)[:8],
                    )
                    await db.refresh(existing_run)
                    return SessionResponse(
                        id=str(existing_run.id),
                        title=(
                            body.title if body and body.title
                            else f"Diagnostik {existing_run.started_at.strftime('%d.%m.%Y')}"
                        ),
                        status=existing_run.status,
                        progress=existing_run.progress,
                        created_at=existing_run.started_at.isoformat(),
                        completed_at=(
                            existing_run.completed_at.isoformat()
                            if existing_run.completed_at else None
                        ),
                    )

        # Create a new DiagnosticRun
        run = DiagnosticRun(
            user_id=user.id,
            diagnostic_id=diagnostic.id,
            token_id=consumed_token.id if consumed_token else None,
            tier="M",
            status="started",
            progress=0.0,
            conversation=[],
            answers={},
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Consume the token (bind to this run)
        if consumed_token and _token_svc:
            try:
                await _token_svc.consume_token(consumed_token.token_code, run.id)
            except ValueError as e:
                logger.error("Token consumption failed: %s", e)
                # Continue anyway — run is already created

        # Start the agent session (generates greeting)
        agent = get_agent()
        async for event in agent.start_session(run):
            pass  # Greeting is persisted by the agent

        # Refresh to get updated data
        await db.refresh(run)

        return SessionResponse(
            id=str(run.id),
            title=(body.title if body and body.title else f"Diagnostik {run.started_at.strftime('%d.%m.%Y')}"),
            status=run.status,
            progress=run.progress,
            created_at=run.started_at.isoformat(),
            completed_at=run.completed_at.isoformat() if run.completed_at else None,
        )

    @router.get("/sessions", response_model=list[SessionResponse])
    async def list_sessions(
        limit: int = 50,
        offset: int = 0,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """List all SCIL sessions for the current user (paginated)."""
        result = await db.execute(
            select(DiagnosticRun)
            .join(Diagnostic)
            .where(
                DiagnosticRun.user_id == user.id,
                Diagnostic.slug == "scil",
                DiagnosticRun.status != "deleted",
            )
            .order_by(desc(DiagnosticRun.started_at))
            .limit(limit)
            .offset(offset)
        )
        runs = result.scalars().all()

        return [
            SessionResponse(
                id=str(r.id),
                title=(r.answers or {}).get("_title") or f"Diagnostik {r.started_at.strftime('%d.%m.%Y %H:%M')}",
                status=r.status,
                progress=r.progress,
                created_at=r.started_at.isoformat(),
                completed_at=r.completed_at.isoformat() if r.completed_at else None,
            )
            for r in runs
        ]

    @router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
    async def get_session(
        session_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get detailed session data including conversation and scores."""
        run = await db.get(DiagnosticRun, session_id)
        if not run or run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        from app.services.scil_scoring import compute_polygon
        from app.services.scil_items import get_cluster_progress

        # Filter out internal keys from answers for polygon computation
        clean_scores = {
            k: v for k, v in (run.answers or {}).items()
            if not k.startswith("_") and isinstance(v, dict)
        }
        polygon = compute_polygon(clean_scores) if clean_scores else None

        # Compute cluster progress from item_responses
        item_responses = run.item_responses or []
        answered_ids = {r["item_id"] for r in item_responses}
        cluster_prog = get_cluster_progress(answered_ids) if answered_ids else None

        # Get persisted suggestions from answers metadata
        answers_data = run.answers or {}
        persisted_suggestions = answers_data.get("_suggestions", None)

        return SessionDetailResponse(
            id=str(run.id),
            title=f"Diagnostik {run.started_at.strftime('%d.%m.%Y %H:%M')}",
            status=run.status,
            progress=run.progress,
            conversation=run.conversation or [],
            scores=clean_scores if clean_scores else None,
            polygon=polygon,
            cluster_progress=cluster_prog,
            items_scored=len(answered_ids),
            items_total=100,
            suggestions=persisted_suggestions,
            created_at=run.started_at.isoformat(),
            completed_at=run.completed_at.isoformat() if run.completed_at else None,
        )

    @router.post("/sessions/{session_id}/message")
    async def send_message(
        session_id: UUID,
        body: SessionMessage,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Send a message to the SCIL agent and get response as SSE stream."""
        # Verify ownership
        run = await db.get(DiagnosticRun, session_id)
        if not run or run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        if run.status == "completed":
            raise HTTPException(status_code=400, detail="Session already completed")

        agent = get_agent()

        async def event_generator():
            async for event in agent.process_message(session_id, body.content):
                yield f"event: message\ndata: {json.dumps(event)}\n\n"
            yield "event: done\ndata: {}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/sessions/{session_id}/stream")
    async def stream_session(
        session_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """SSE endpoint for real-time session updates."""
        run = await db.get(DiagnosticRun, session_id)
        if not run or run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        from app.services.scil_scoring import compute_polygon

        async def status_stream():
            # Send current state
            polygon = compute_polygon(run.answers) if run.answers else None
            state = {
                "type": "session_state",
                "status": run.status,
                "progress": run.progress,
                "scores": run.answers,
                "polygon": polygon,
            }
            yield f"event: message\ndata: {json.dumps(state)}\n\n"

        return StreamingResponse(
            status_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.patch("/sessions/{session_id}")
    async def update_session(
        session_id: UUID,
        body: SessionUpdate,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Rename a session."""
        run = await db.get(DiagnosticRun, session_id)
        if not run or run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        # Store title in answers JSONB (lightweight, no schema change)
        answers = dict(run.answers or {})
        if body.title is not None:
            answers["_title"] = body.title
            run.answers = answers
        await db.commit()
        return {"status": "updated"}

    @router.delete("/sessions/{session_id}")
    async def delete_session(
        session_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Soft-delete a session."""
        run = await db.get(DiagnosticRun, session_id)
        if not run or run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")

        run.status = "deleted"
        await db.commit()
        return {"status": "deleted"}

    @router.get("/sessions/{session_id}/result", response_model=ResultResponse)
    async def get_result(
        session_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get the final assessment result for a completed session."""
        run = await db.get(DiagnosticRun, session_id)
        if not run or run.user_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
        if run.status != "completed":
            raise HTTPException(status_code=400, detail="Session not yet completed")

        result = await db.execute(
            select(DiagnosticResult).where(DiagnosticResult.run_id == session_id)
        )
        dr = result.scalar_one_or_none()
        if not dr:
            raise HTTPException(status_code=404, detail="Result not found")

        return ResultResponse(
            id=str(dr.id),
            scores=dr.scores,
            summary=dr.summary,
            recommendations=dr.recommendations,
            polygon_data=dr.polygon_data,
            created_at=dr.created_at.isoformat(),
        )

    return router
