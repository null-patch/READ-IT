from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageReadResponse(BaseModel):
    id: UUID
    message_id: UUID
    user_id: UUID
    read_at: datetime

    model_config = ConfigDict(from_attributes=True)
