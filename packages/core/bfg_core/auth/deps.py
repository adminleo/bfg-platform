from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.auth.jwt import verify_token
from bfg_core.models.user import User

security = HTTPBearer()


def get_current_user_dependency(secret_key: str, algorithm: str = "HS256"):
    """Factory that returns a get_current_user dependency with injected config."""

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(),
    ) -> User:
        payload = verify_token(credentials.credentials, secret_key, algorithm)
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

    return get_current_user


# Default dependency — products override with their own config
async def get_current_user() -> User:
    raise NotImplementedError("Products must configure get_current_user via get_current_user_dependency()")
