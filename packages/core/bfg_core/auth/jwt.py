from datetime import datetime, timedelta
from uuid import UUID

from jose import jwt, JWTError


def create_access_token(
    user_id: UUID,
    secret_key: str,
    algorithm: str = "HS256",
    expire_minutes: int = 1440,
    extra_claims: dict | None = None,
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def verify_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None
