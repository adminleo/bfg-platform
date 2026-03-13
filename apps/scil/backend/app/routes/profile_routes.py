"""Profile routes — User profile management and history.

Endpoints:
    GET    /me              - Current user profile
    PATCH  /me              - Update full_name, bio
    POST   /me/password     - Change password
    GET    /me/coach        - Get assigned coach info
    GET    /me/codes        - User's diagnostic codes
    GET    /me/history      - Diagnostic history with results
"""

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.models.user import User
from bfg_core.models.coach import CoachAssignment, AssignmentStatus
from bfg_core.models.token import DiagnosticToken, TokenStatus
from bfg_core.models.diagnostic import DiagnosticRun, DiagnosticResult

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    bio: str | None = None
    created_at: str


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    bio: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class CoachInfoResponse(BaseModel):
    coach_name: str
    coach_email: str
    assignment_status: str
    assigned_at: str


class UserCodeResponse(BaseModel):
    id: str
    token_code: str
    status: str
    diagnostic_type: str
    tier: str
    created_at: str
    activated_at: str | None = None
    consumed_at: str | None = None


class HistoryItem(BaseModel):
    id: str
    status: str
    progress: float
    started_at: str
    completed_at: str | None = None
    scores: dict | None = None
    polygon_data: dict | None = None


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_profile_routes(get_db, get_current_user, token_service):
    """Factory to create profile routes.

    Args:
        get_db: FastAPI dependency for DB session
        get_current_user: FastAPI dependency for authenticated user
        token_service: callable returning TokenService (lazy init)
    """
    router = APIRouter(prefix="/me", tags=["profile"])

    def _tokens():
        return token_service() if callable(token_service) else token_service

    @router.get("", response_model=ProfileResponse)
    async def get_profile(
        user: User = Depends(get_current_user),
    ):
        """Get current user profile."""
        return ProfileResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            bio=user.bio,
            created_at=user.created_at.isoformat(),
        )

    @router.patch("", response_model=ProfileResponse)
    async def update_profile(
        body: ProfileUpdateRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Update profile fields."""
        if body.full_name is not None:
            user.full_name = body.full_name
        if body.bio is not None:
            user.bio = body.bio
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)

        return ProfileResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            bio=user.bio,
            created_at=user.created_at.isoformat(),
        )

    @router.post("/password")
    async def change_password(
        body: PasswordChangeRequest,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Change password (requires current password)."""
        if not pwd_context.verify(body.current_password, user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Aktuelles Passwort ist falsch.",
            )

        if len(body.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Neues Passwort muss mindestens 6 Zeichen haben.",
            )

        user.hashed_password = pwd_context.hash(body.new_password)
        user.updated_at = datetime.utcnow()
        await db.commit()

        return {"status": "updated", "message": "Passwort erfolgreich geaendert."}

    @router.get("/coach", response_model=CoachInfoResponse | None)
    async def get_coach_info(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get the user's assigned coach info (if any)."""
        result = await db.execute(
            select(CoachAssignment)
            .where(
                CoachAssignment.coachee_id == user.id,
                CoachAssignment.status.in_([
                    AssignmentStatus.PENDING,
                    AssignmentStatus.ACTIVE,
                    AssignmentStatus.COMPLETED,
                ]),
            )
            .order_by(desc(CoachAssignment.created_at))
            .limit(1)
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            return None

        coach = await db.get(User, assignment.coach_id)
        if not coach:
            return None

        return CoachInfoResponse(
            coach_name=coach.full_name,
            coach_email=coach.email,
            assignment_status=assignment.status.value,
            assigned_at=assignment.created_at.isoformat(),
        )

    @router.get("/codes", response_model=list[UserCodeResponse])
    async def get_codes(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get user's diagnostic codes."""
        result = await db.execute(
            select(DiagnosticToken)
            .where(DiagnosticToken.user_id == user.id)
            .order_by(desc(DiagnosticToken.created_at))
        )
        tokens = result.scalars().all()

        return [
            UserCodeResponse(
                id=str(t.id),
                token_code=t.token_code[:16] + "...",
                status=t.status.value,
                diagnostic_type=t.diagnostic_type,
                tier=t.tier.value,
                created_at=t.created_at.isoformat(),
                activated_at=t.activated_at.isoformat() if t.activated_at else None,
                consumed_at=t.consumed_at.isoformat() if t.consumed_at else None,
            )
            for t in tokens
        ]

    @router.get("/history", response_model=list[HistoryItem])
    async def get_history(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        """Get user's diagnostic run history."""
        result = await db.execute(
            select(DiagnosticRun)
            .where(
                DiagnosticRun.user_id == user.id,
                DiagnosticRun.status != "deleted",
            )
            .order_by(desc(DiagnosticRun.started_at))
        )
        runs = result.scalars().all()

        items = []
        for run in runs:
            scores = None
            polygon_data = None

            if run.status == "completed":
                dr_result = await db.execute(
                    select(DiagnosticResult).where(DiagnosticResult.run_id == run.id)
                )
                dr = dr_result.scalar_one_or_none()
                if dr:
                    scores = dr.scores
                    polygon_data = dr.polygon_data

            items.append(HistoryItem(
                id=str(run.id),
                status=run.status,
                progress=run.progress,
                started_at=run.started_at.isoformat(),
                completed_at=run.completed_at.isoformat() if run.completed_at else None,
                scores=scores,
                polygon_data=polygon_data,
            ))

        return items

    return router
