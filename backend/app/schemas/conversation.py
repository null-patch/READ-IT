from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    type: str
    title: Optional[str] = None
    created_by: UUID


class ConversationResponse(BaseModel):
    id: UUID
    type: str
    title: Optional[str]
    created_by: Optional[UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
