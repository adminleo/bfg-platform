from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.auth.jwt import create_access_token
from bfg_core.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "trainee"


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


def create_auth_routes(
    get_db,
    secret_key: str,
    algorithm: str = "HS256",
    expire_minutes: int = 1440,
) -> APIRouter:
    """Factory that creates auth routes with injected dependencies."""
    auth = APIRouter(prefix="/auth", tags=["auth"])

    @auth.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        # Self-registration restricted to trainee role.
        # Coach/admin roles require promotion by an admin.
        safe_role = "trainee"
        user = User(
            email=data.email,
            hashed_password=pwd_context.hash(data.password),
            full_name=data.full_name,
            role=safe_role,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @auth.post("/login", response_model=AuthToken)
    async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db),
    ):
        """Login with form-urlencoded data (username=email, password)."""
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalar_one_or_none()
        if not user or not pwd_context.verify(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
        token = create_access_token(
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
        return AuthToken(access_token=token)

    return auth
