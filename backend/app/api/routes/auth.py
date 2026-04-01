import time
from collections import defaultdict
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import jwt
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, AuthToken

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Rate limiter (references the global instance via app.state) ──
limiter = Limiter(key_func=get_remote_address)

# ── Brute-force protection ───────────────────────────────────
_failed_attempts: dict[str, list[float]] = defaultdict(list)
_LOCKOUT_THRESHOLD = 5
_LOCKOUT_WINDOW = 900  # 15 minutes


def _check_brute_force(email: str) -> None:
    """Raise 429 if too many failed login attempts in the window."""
    now = time.time()
    attempts = _failed_attempts[email]
    # Prune old attempts
    _failed_attempts[email] = [t for t in attempts if now - t < _LOCKOUT_WINDOW]
    if len(_failed_attempts[email]) >= _LOCKOUT_THRESHOLD:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again in 15 minutes.",
        )


def create_access_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=AuthToken)
@limiter.limit("5/minute")
async def login(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    _check_brute_force(data.email)

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        _failed_attempts[data.email].append(time.time())
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Clear failed attempts on success
    _failed_attempts.pop(data.email, None)
    return AuthToken(access_token=create_access_token(user.id))
