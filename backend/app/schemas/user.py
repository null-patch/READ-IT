from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    display_name: str
    email: EmailStr | None = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    display_name: str
    email: EmailStr | None = None
    avatar_url: str | None = None
    bio: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
