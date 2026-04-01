from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "trainee"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
