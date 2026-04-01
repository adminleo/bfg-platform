"""Invitation routes — Accept coach invitations and register as coachee.

Endpoints:
    GET    /invite/{token}         - Validate invitation, return coach info
    POST   /invite/{token}/accept  - Register + link to coach + activate code → JWT
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.auth.jwt import create_access_token
from bfg_core.models.user import User
from bfg_core.models.coach import CoachAssignment, AssignmentStatus
from bfg_core.models.token import DiagnosticToken, TokenStatus

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class InvitationInfoResponse(BaseModel):
    coach_name: str
    coach_email: str
    coachee_email: str
    has_code: bool
    status: str


class AcceptInvitationRequest(BaseModel):
    full_name: str
    password: str
    email: EmailStr | None = None  # Optional: override invitation email


class AcceptInvitationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    message: str


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_invitation_routes(get_db, token_service, secret_key, algorithm, expire_minutes):
    """Factory to create invitation routes.

    Args:
        get_db: FastAPI dependency for DB session
        token_service: callable returning TokenService (lazy init)
        secret_key: JWT secret key
        algorithm: JWT algorithm
        expire_minutes: JWT expiration
    """
    router = APIRouter(prefix="/invite", tags=["invitation"])

    def _tokens():
        return token_service() if callable(token_service) else token_service

    @router.get("/{invitation_token}", response_model=InvitationInfoResponse)
    async def get_invitation_info(
        invitation_token: str,
        db: AsyncSession = Depends(get_db),
    ):
        """Validate an invitation token and return coach info."""
        result = await db.execute(
            select(CoachAssignment)
            .where(CoachAssignment.invitation_token == invitation_token)
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(status_code=404, detail="Einladung nicht gefunden oder abgelaufen.")

        if assignment.status not in (AssignmentStatus.INVITED, AssignmentStatus.PENDING):
            raise HTTPException(
                status_code=400,
                detail="Diese Einladung wurde bereits angenommen.",
            )

        # Get coach info
        coach = await db.get(User, assignment.coach_id)
        if not coach:
            raise HTTPException(status_code=500, detail="Coach nicht gefunden.")

        has_code = assignment.token_id is not None

        return InvitationInfoResponse(
            coach_name=coach.full_name,
            coach_email=coach.email,
            coachee_email=assignment.coachee_email,
            has_code=has_code,
            status=assignment.status.value,
        )

    @router.post("/{invitation_token}/accept", response_model=AcceptInvitationResponse)
    async def accept_invitation(
        invitation_token: str,
        body: AcceptInvitationRequest,
        db: AsyncSession = Depends(get_db),
    ):
        """Accept an invitation: register as coachee, link to coach, activate code."""
        # Find assignment
        result = await db.execute(
            select(CoachAssignment)
            .where(CoachAssignment.invitation_token == invitation_token)
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(status_code=404, detail="Einladung nicht gefunden oder abgelaufen.")

        if assignment.status not in (AssignmentStatus.INVITED, AssignmentStatus.PENDING):
            raise HTTPException(
                status_code=400,
                detail="Diese Einladung wurde bereits angenommen.",
            )

        # Use the email from the body (if provided) or from the invitation
        email = (body.email or assignment.coachee_email).lower()

        # Check if user already exists
        existing = await db.execute(select(User).where(User.email == email))
        user = existing.scalar_one_or_none()

        if user:
            # Existing user — just link them to the coach
            logger.info("Existing user %s accepting invitation", email)
        else:
            # Create new user
            user = User(
                email=email,
                hashed_password=pwd_context.hash(body.password),
                full_name=body.full_name,
                role="trainee",
            )
            db.add(user)
            await db.flush()  # Get user.id
            logger.info("New user %s registered via invitation", email)

        # Link coachee to assignment
        assignment.coachee_id = user.id
        assignment.status = AssignmentStatus.PENDING

        # Commit user + assignment first (TokenService uses its own session)
        await db.commit()
        await db.refresh(user)

        # If there's an assigned code, activate it for the coachee
        if assignment.token_id:
            token_svc = _tokens()
            if token_svc:
                token = await db.get(DiagnosticToken, assignment.token_id)
                if token and token.status in (
                    TokenStatus.EMITTED, TokenStatus.SOLD, TokenStatus.ASSIGNED,
                ):
                    try:
                        await token_svc.activate_token(token.token_code, user.id)
                        assignment.status = AssignmentStatus.ACTIVE
                        await db.commit()
                        logger.info("Token activated for coachee %s", email)
                    except ValueError as e:
                        logger.error("Token activation failed: %s", e)
                        # Continue — user is registered but code not activated

        # Generate JWT
        access_token = create_access_token(
            user.id,
            secret_key,
            algorithm,
            expire_minutes,
            extra_claims={
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            },
        )

        return AcceptInvitationResponse(
            access_token=access_token,
            user_id=str(user.id),
            message="Einladung angenommen. Willkommen bei SCIL!",
        )

    return router
