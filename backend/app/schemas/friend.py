from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict


class FriendStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class FriendRequestCreate(BaseModel):
    addressee_id: UUID


class FriendRequestResponse(BaseModel):
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: FriendStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FriendActionResponse(BaseModel):
    success: bool
    message: str


class FriendListItem(BaseModel):
    id: UUID
    username: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None
    status: str

    model_config = ConfigDict(from_attributes=True)
