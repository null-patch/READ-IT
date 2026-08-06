from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ConversationCreate(BaseModel):
    type: str
    title: str | None = None
    participant_ids: list[UUID]


class ConversationResponse(BaseModel):
    id: UUID
    type: str
    title: str | None = None
    created_by: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationMemberResponse(BaseModel):
    conversation_id: UUID
    user_id: UUID
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddParticipantRequest(BaseModel):
    user_id: UUID


class RemoveParticipantRequest(BaseModel):
    user_id: UUID