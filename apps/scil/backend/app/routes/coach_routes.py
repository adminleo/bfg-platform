"""Coach Dashboard API routes — manage coachees, codes, and invitations.

Endpoints:
    GET    /coach/dashboard           - Dashboard stats
    GET    /coach/coachees            - List all coachee assignments
    GET    /coach/coachees/{id}       - Coachee detail with diagnostics
    POST   /coach/invite              - Invite coachee (assign code + send email)
    GET    /coach/codes               - Coach's code inventory
    POST   /coach/codes/assign        - Manually assign code to coachee
    GET    /coach/activity            - Recent activity feed

All endpoints require role "coach" or "admin".
"""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bfg_core.models.user import User
from bfg_core.models.coach import CoachAssignment, AssignmentStatus
from bfg_core.models.token import DiagnosticToken, TokenStatus
from bfg_core.models.diagnostic import DiagnosticRun, DiagnosticResult
from bfg_core.auth.rbac import require_role

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class InviteRequest(BaseModel):
    email: EmailStr
    notes: str | None = None
    token_id: UUID | None = None  # Optional: pre-assign a specific code


class AssignCodeRequest(BaseModel):
    assignment_id: UUID
    token_id: UUID


class DashboardResponse(BaseModel):
    total_coachees: int
    active_diagnostics: int
    codes_available: int
    completed_diagnostics: int
    recent_invitations: int


class CoacheeListItem(BaseModel):
    id: str
    coachee_email: str
    coachee_name: str | None = None
    status: str
    has_diagnostic: bool = False
    last_activity: str | None = None
    created_at: str
    notes: str | None = None


class CoacheeDetailResponse(BaseModel):
    id: str
    coachee_email: str
    coachee_name: str | None = None
    status: str
    notes: str | None = None
    created_at: str
    updated_at: str
    # Diagnostic data
    diagnostic_runs: list[dict] = []
    latest_scores: dict | None = None
    latest_polygon: dict | None = None
    # Code info
    token_code: str | None = None
    token_status: str | None = None


class CodeInventoryItem(BaseModel):
    id: str
    token_code: str
    status: str
    diagnostic_type: str
    tier: str
    created_at: str
    assigned_to: str | None = None


class ActivityItem(BaseModel):
    type: str  # "invitation", "activation", "completion"
    description: str
    timestamp: str
    coachee_email: str | None = None


class InviteResponse(BaseModel):
    id: str
    coachee_email: str
    status: str
    invitation_token: str | None = None
    message: str


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_coach_routes(get_db, get_current_user, token_service, email_service):
    """Factory to create coach routes with injected dependencies.

    Args:
        get_db: FastAPI dependency for DB session
        get_current_user: FastAPI dependency for authenticated user
        token_service: callable returning TokenService (lazy init)
        email_service: callable returning EmailService or None (lazy init)
    """
    router = APIRouter(prefix="/coach", tags=["coach"])

    def _tokens():
        return token_service() if callable(token_service) else token_service

    def _email():
        return email_service() if callable(email_service) else email_service

    @router.get("/dashboard", response_model=DashboardResponse)
    async def get_dashboard(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get coach dashboard statistics."""
        require_role(user, "coach", "admin")
        coach_id = user.id

        # Total coachees
        total = await db.execute(
            select(func.count(CoachAssignment.id))
            .where(CoachAssignment.coach_id == coach_id)
        )
        total_coachees = total.scalar() or 0

        # Active diagnostics (assignments in ACTIVE status)
        active = await db.execute(
            select(func.count(CoachAssignment.id))
            .where(
                CoachAssignment.coach_id == coach_id,
                CoachAssignment.status == AssignmentStatus.ACTIVE,
            )
        )
        active_diagnostics = active.scalar() or 0

        # Available codes (tokens owned by coach, not yet consumed)
        available = await db.execute(
            select(func.count(DiagnosticToken.id))
            .where(
                DiagnosticToken.sold_by_expert_id == coach_id,
                DiagnosticToken.status.in_([
                    TokenStatus.EMITTED, TokenStatus.SOLD, TokenStatus.ASSIGNED,
                ]),
            )
        )
        codes_available = available.scalar() or 0

        # Completed diagnostics
        completed = await db.execute(
            select(func.count(CoachAssignment.id))
            .where(
                CoachAssignment.coach_id == coach_id,
                CoachAssignment.status == AssignmentStatus.COMPLETED,
            )
        )
        completed_diagnostics = completed.scalar() or 0

        # Recent invitations (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent = await db.execute(
            select(func.count(CoachAssignment.id))
            .where(
                CoachAssignment.coach_id == coach_id,
                CoachAssignment.status == AssignmentStatus.INVITED,
                CoachAssignment.created_at >= thirty_days_ago,
            )
        )
        recent_invitations = recent.scalar() or 0

        return DashboardResponse(
            total_coachees=total_coachees,
            active_diagnostics=active_diagnostics,
            codes_available=codes_available,
            completed_diagnostics=completed_diagnostics,
            recent_invitations=recent_invitations,
        )

    @router.get("/coachees", response_model=list[CoacheeListItem])
    async def list_coachees(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """List all coachee assignments for the current coach."""
        require_role(user, "coach", "admin")
        result = await db.execute(
            select(CoachAssignment)
            .options(selectinload(CoachAssignment.coachee))
            .where(CoachAssignment.coach_id == user.id)
            .order_by(desc(CoachAssignment.created_at))
        )
        assignments = result.scalars().all()

        items = []
        for a in assignments:
            coachee_name = a.coachee.full_name if a.coachee else None

            # Check if coachee has an active diagnostic
            has_diag = False
            last_activity = None
            if a.coachee_id:
                run_result = await db.execute(
                    select(DiagnosticRun)
                    .where(DiagnosticRun.user_id == a.coachee_id)
                    .order_by(desc(DiagnosticRun.started_at))
                    .limit(1)
                )
                latest_run = run_result.scalar_one_or_none()
                if latest_run:
                    has_diag = True
                    last_activity = latest_run.started_at.isoformat()

            items.append(CoacheeListItem(
                id=str(a.id),
                coachee_email=a.coachee_email,
                coachee_name=coachee_name,
                status=a.status.value,
                has_diagnostic=has_diag,
                last_activity=last_activity or a.updated_at.isoformat(),
                created_at=a.created_at.isoformat(),
                notes=a.notes,
            ))

        return items

    @router.get("/coachees/{assignment_id}", response_model=CoacheeDetailResponse)
    async def get_coachee_detail(
        assignment_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get detailed coachee information including diagnostics."""
        require_role(user, "coach", "admin")
        result = await db.execute(
            select(CoachAssignment)
            .options(
                selectinload(CoachAssignment.coachee),
                selectinload(CoachAssignment.token),
            )
            .where(
                CoachAssignment.id == assignment_id,
                CoachAssignment.coach_id == user.id,
            )
        )
        assignment = result.scalar_one_or_none()
        if not assignment:
            raise HTTPException(status_code=404, detail="Coachee-Zuweisung nicht gefunden")

        # Fetch diagnostic runs for this coachee
        runs_data = []
        latest_scores = None
        latest_polygon = None

        if assignment.coachee_id:
            runs_result = await db.execute(
                select(DiagnosticRun)
                .where(
                    DiagnosticRun.user_id == assignment.coachee_id,
                    DiagnosticRun.status != "deleted",
                )
                .order_by(desc(DiagnosticRun.started_at))
            )
            runs = runs_result.scalars().all()

            for run in runs:
                run_info = {
                    "id": str(run.id),
                    "status": run.status,
                    "progress": run.progress,
                    "started_at": run.started_at.isoformat(),
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                }

                # Get result if completed
                if run.status == "completed":
                    res_result = await db.execute(
                        select(DiagnosticResult).where(DiagnosticResult.run_id == run.id)
                    )
                    dr = res_result.scalar_one_or_none()
                    if dr:
                        run_info["scores"] = dr.scores
                        run_info["polygon_data"] = dr.polygon_data
                        # Use most recent completed run for latest data
                        if latest_scores is None:
                            latest_scores = dr.scores
                            latest_polygon = dr.polygon_data

                runs_data.append(run_info)

        # Token info
        token_code = None
        token_status = None
        if assignment.token:
            token_code = assignment.token.token_code[:16] + "..."
            token_status = assignment.token.status.value

        return CoacheeDetailResponse(
            id=str(assignment.id),
            coachee_email=assignment.coachee_email,
            coachee_name=assignment.coachee.full_name if assignment.coachee else None,
            status=assignment.status.value,
            notes=assignment.notes,
            created_at=assignment.created_at.isoformat(),
            updated_at=assignment.updated_at.isoformat(),
            diagnostic_runs=runs_data,
            latest_scores=latest_scores,
            latest_polygon=latest_polygon,
            token_code=token_code,
            token_status=token_status,
        )

    @router.post("/invite", response_model=InviteResponse)
    async def invite_coachee(
        body: InviteRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Invite a coachee: create assignment, optionally assign code, send email."""
        require_role(user, "coach", "admin")
        # Check for duplicate invitation
        existing = await db.execute(
            select(CoachAssignment).where(
                CoachAssignment.coach_id == user.id,
                CoachAssignment.coachee_email == body.email.lower(),
                CoachAssignment.status.in_([
                    AssignmentStatus.INVITED,
                    AssignmentStatus.PENDING,
                    AssignmentStatus.ACTIVE,
                ]),
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Dieser Coachee wurde bereits eingeladen.",
            )

        # If a specific token is provided, verify it belongs to the coach
        token_id = None
        if body.token_id:
            token_result = await db.execute(
                select(DiagnosticToken).where(
                    DiagnosticToken.id == body.token_id,
                    DiagnosticToken.sold_by_expert_id == user.id,
                    DiagnosticToken.status.in_([
                        TokenStatus.EMITTED, TokenStatus.SOLD,
                    ]),
                )
            )
            token = token_result.scalar_one_or_none()
            if not token:
                raise HTTPException(
                    status_code=400,
                    detail="Code nicht gefunden oder nicht verfuegbar.",
                )
            token_id = token.id
            # Mark as assigned
            token.status = TokenStatus.ASSIGNED
            await db.flush()

        # Create assignment
        invitation_token = CoachAssignment.generate_invitation_token()
        assignment = CoachAssignment(
            coach_id=user.id,
            coachee_email=body.email.lower(),
            invitation_token=invitation_token,
            token_id=token_id,
            status=AssignmentStatus.INVITED,
            notes=body.notes,
        )
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        # Send invitation email
        email_svc = _email()
        if email_svc:
            try:
                from bfg_core.config import CoreSettings
                frontend_url = "http://localhost:3000"  # Will be overridden by settings
                invitation_url = f"{frontend_url}/invite/{invitation_token}"

                await email_svc.send_template(
                    body.email.lower(),
                    "coach_invitation",
                    {
                        "coach_name": user.full_name,
                        "invitation_url": invitation_url,
                    },
                )
                logger.info("Invitation email sent to %s", body.email)
            except Exception as e:
                logger.error("Failed to send invitation email: %s", e)
                # Don't fail the invitation if email fails

        return InviteResponse(
            id=str(assignment.id),
            coachee_email=assignment.coachee_email,
            status=assignment.status.value,
            invitation_token=invitation_token,
            message=f"Einladung an {body.email} gesendet.",
        )

    @router.get("/codes", response_model=list[CodeInventoryItem])
    async def list_codes(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """List the coach's code inventory (tokens they purchased)."""
        require_role(user, "coach", "admin")
        result = await db.execute(
            select(DiagnosticToken)
            .where(DiagnosticToken.sold_by_expert_id == user.id)
            .order_by(desc(DiagnosticToken.created_at))
        )
        tokens = result.scalars().all()

        items = []
        for t in tokens:
            # Check if assigned to a coachee
            assigned_to = None
            if t.status == TokenStatus.ASSIGNED:
                assign_result = await db.execute(
                    select(CoachAssignment.coachee_email)
                    .where(CoachAssignment.token_id == t.id)
                )
                row = assign_result.scalar_one_or_none()
                if row:
                    assigned_to = row

            items.append(CodeInventoryItem(
                id=str(t.id),
                token_code=t.token_code[:16] + "...",
                status=t.status.value,
                diagnostic_type=t.diagnostic_type,
                tier=t.tier.value,
                created_at=t.created_at.isoformat(),
                assigned_to=assigned_to,
            ))

        return items

    @router.post("/codes/assign")
    async def assign_code(
        body: AssignCodeRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Manually assign a code to an existing coachee assignment."""
        require_role(user, "coach", "admin")
        # Verify assignment belongs to coach
        assignment = await db.get(CoachAssignment, body.assignment_id)
        if not assignment or assignment.coach_id != user.id:
            raise HTTPException(status_code=404, detail="Zuweisung nicht gefunden")

        if assignment.token_id:
            raise HTTPException(
                status_code=400,
                detail="Diesem Coachee wurde bereits ein Code zugewiesen.",
            )

        # Verify token belongs to coach and is available
        token_result = await db.execute(
            select(DiagnosticToken).where(
                DiagnosticToken.id == body.token_id,
                DiagnosticToken.sold_by_expert_id == user.id,
                DiagnosticToken.status.in_([
                    TokenStatus.EMITTED, TokenStatus.SOLD,
                ]),
            )
        )
        token = token_result.scalar_one_or_none()
        if not token:
            raise HTTPException(
                status_code=400,
                detail="Code nicht gefunden oder nicht verfuegbar.",
            )

        # Assign
        token.status = TokenStatus.ASSIGNED
        assignment.token_id = token.id
        assignment.updated_at = datetime.utcnow()
        await db.commit()

        return {"status": "assigned", "message": "Code wurde zugewiesen."}

    @router.get("/activity", response_model=list[ActivityItem])
    async def get_activity(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get recent activity feed for the coach."""
        require_role(user, "coach", "admin")
        activities: list[ActivityItem] = []

        # Recent assignments (all statuses)
        result = await db.execute(
            select(CoachAssignment)
            .where(CoachAssignment.coach_id == user.id)
            .order_by(desc(CoachAssignment.updated_at))
            .limit(20)
        )
        assignments = result.scalars().all()

        for a in assignments:
            if a.status == AssignmentStatus.INVITED:
                activities.append(ActivityItem(
                    type="invitation",
                    description=f"Einladung an {a.coachee_email} gesendet",
                    timestamp=a.created_at.isoformat(),
                    coachee_email=a.coachee_email,
                ))
            elif a.status == AssignmentStatus.ACTIVE:
                activities.append(ActivityItem(
                    type="activation",
                    description=f"{a.coachee_email} hat die Diagnostik gestartet",
                    timestamp=a.updated_at.isoformat(),
                    coachee_email=a.coachee_email,
                ))
            elif a.status == AssignmentStatus.COMPLETED:
                activities.append(ActivityItem(
                    type="completion",
                    description=f"{a.coachee_email} hat die Diagnostik abgeschlossen",
                    timestamp=a.updated_at.isoformat(),
                    coachee_email=a.coachee_email,
                ))

        # Sort by timestamp descending
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:20]

    return router
