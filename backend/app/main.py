import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.database import engine, Base, async_session
from app.core.seed import seed_diagnostics
from app.api.routes import auth, tokens, diagnostics, experts
from app.api.routes import feedback, import_results

# ── Rate limiter ─────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


# ── Security headers middleware ──────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as db:
        await seed_diagnostics(db)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Gr8hub API",
    version="0.2.0",
    lifespan=lifespan,
)

# ── Rate limiter wiring ──────────────────────────────────────
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


# ── Middleware ────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# CORS — restrict to known origins; configurable via ALLOWED_ORIGINS env var
_allowed_origins = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# ── Routes ────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tokens.router, prefix="/api/v1")
app.include_router(diagnostics.router, prefix="/api/v1")
app.include_router(experts.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(import_results.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gr8hub-api"}
