from uuid import UUID
from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class MediaUploadResponse(BaseModel):
    id: UUID
    message_id: UUID
    uploader_id: UUID
    media_type: str
    original_name: str
    stored_name: str
    mime_type: str
    file_size: int
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MediaResponse(MediaUploadResponse):
    pass


class MediaListResponse(BaseModel):
    items: list[MediaResponse]
    total: int


class UploadUrlResponse(BaseModel):
    upload_url: str
    file_name: str


class DeleteMediaResponse(BaseModel):
    success: bool
    message: str
