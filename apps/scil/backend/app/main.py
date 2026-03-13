"""SCIL Profile — FastAPI Application.

Mounts shared auth routes from bfg_core and SCIL-specific diagnostic routes.
Initializes AIService, DiagnosisAgent, and seeds the SCIL diagnostic on startup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from bfg_core.database import create_engine_and_session, Base
from bfg_core.auth.routes import create_auth_routes
from bfg_core.auth.deps import get_current_user_dependency
from bfg_core.services.ai_service import AIService
from bfg_core.services.token_service import TokenService
from bfg_core.services.stripe_service import StripeService
from bfg_core.services.email_service import EmailService

# Import all models so SQLAlchemy knows about them
import bfg_core.models  # noqa: F401

logger = logging.getLogger(__name__)

engine, async_session = create_engine_and_session(settings.database_url, settings.debug)

# -- Services (initialized in lifespan) --
ai_service: AIService | None = None
diagnosis_agent = None
token_service: TokenService | None = None
stripe_service: StripeService | None = None
email_service: EmailService | None = None


async def get_db():
    async with async_session() as session:
        yield session


# Auth dependency with injected config
_get_current_user = get_current_user_dependency(
    secret_key=settings.secret_key,
    algorithm=settings.algorithm,
)


async def get_current_user(
    user=Depends(_get_current_user),
    db=Depends(get_db),
):
    """Wrap the factory dependency to inject get_db properly."""
    # The factory dependency already resolves the user.
    # We need to re-implement slightly because the factory's inner function
    # expects db via Depends() but we need to wire our get_db.
    return user


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_service, diagnosis_agent, token_service, stripe_service, email_service

    # Create tables (idempotent, will be replaced by Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize AI Service
    ai_service = AIService(settings, async_session)
    logger.info(
        "AIService initialized: mode=%s, configured=%s",
        settings.llm_mode,
        ai_service.is_configured(),
    )

    # Initialize Token Service
    token_service = TokenService(async_session, settings.token_hmac_secret)
    logger.info("TokenService initialized")

    # Initialize Stripe Service
    stripe_service = StripeService(settings, token_service)
    logger.info(
        "StripeService initialized: configured=%s",
        stripe_service.is_configured,
    )

    # Initialize Email Service
    email_service = EmailService(settings)
    logger.info("EmailService initialized")

    # Initialize Diagnosis Agent
    from app.agents.diagnosis_agent import DiagnosisAgent
    diagnosis_agent = DiagnosisAgent(ai_service, async_session)

    # Seed SCIL diagnostic
    from app.services.scil_seed import seed_scil_diagnostic
    async with async_session() as session:
        diag = await seed_scil_diagnostic(session)
        logger.info("SCIL diagnostic seeded: id=%s, slug=%s", diag.id, diag.slug)

    yield

    await engine.dispose()


app = FastAPI(
    title="SCIL Profile API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# -- Auth routes from shared core --
auth_router = create_auth_routes(
    get_db=get_db,
    secret_key=settings.secret_key,
    algorithm=settings.algorithm,
    expire_minutes=settings.access_token_expire_minutes,
)
app.include_router(auth_router, prefix="/api/v1")


# -- SCIL routes --
# We need a custom get_current_user that properly injects get_db
def _scil_get_current_user():
    """Create a get_current_user dependency wired to our get_db."""
    from bfg_core.auth.jwt import verify_token
    from bfg_core.models.user import User
    from fastapi import HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from sqlalchemy import select
    from uuid import UUID

    security = HTTPBearer()

    async def dep(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db=Depends(get_db),
    ) -> User:
        payload = verify_token(credentials.credentials, settings.secret_key, settings.algorithm)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user

    return dep


from app.routes.scil_routes import create_scil_routes
from app.routes.payment_routes import create_payment_routes
from app.routes.coach_routes import create_coach_routes
from app.routes.invitation_routes import create_invitation_routes
from app.routes.profile_routes import create_profile_routes

scil_router = create_scil_routes(
    get_db=get_db,
    get_current_user=_scil_get_current_user(),
    get_agent=lambda: diagnosis_agent,
    token_service=lambda: token_service,
)
app.include_router(scil_router, prefix="/api/v1")

# -- Payment/Code routes --
payment_router = create_payment_routes(
    get_db=get_db,
    get_current_user=_scil_get_current_user(),
    stripe_service=lambda: stripe_service,
    token_service=lambda: token_service,
)
app.include_router(payment_router, prefix="/api/v1")

# -- Coach routes --
coach_router = create_coach_routes(
    get_db=get_db,
    get_current_user=_scil_get_current_user(),
    token_service=lambda: token_service,
    email_service=lambda: email_service,
)
app.include_router(coach_router, prefix="/api/v1")

# -- Invitation routes (public) --
invitation_router = create_invitation_routes(
    get_db=get_db,
    token_service=lambda: token_service,
    secret_key=settings.secret_key,
    algorithm=settings.algorithm,
    expire_minutes=settings.access_token_expire_minutes,
)
app.include_router(invitation_router, prefix="/api/v1")

# -- Profile routes --
profile_router = create_profile_routes(
    get_db=get_db,
    get_current_user=_scil_get_current_user(),
    token_service=lambda: token_service,
)
app.include_router(profile_router, prefix="/api/v1")


# -- Health check --
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "scil-profile-api",
        "ai_configured": ai_service.is_configured() if ai_service else False,
    }
