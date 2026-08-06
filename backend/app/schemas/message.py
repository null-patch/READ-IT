from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class MessageCreate(BaseModel):
    conversation_id: UUID
    content: str
    message_type: str = "text"


class MessageUpdate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID | None
    message_type: str
    content: str | None
    edited: bool
    deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TypingEvent(BaseModel):
    conversation_id: UUID


class ReadReceipt(BaseModel):
    conversation_id: UUID
    message_id: UUID


class PresenceEvent(BaseModel):
    user_id: UUID
    online: bool


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int