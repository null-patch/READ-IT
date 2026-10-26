from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.media import (
    DeleteMediaResponse,
    MediaResponse,
)
from app.services.media import MediaService

router = APIRouter(
    prefix="/media",
    tags=["Media"],
)


@router.post(
    "/upload/{message_id}",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_media(
    message_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MediaService.upload(
        db=db,
        file=file,
        message_id=message_id,
        uploader_id=current_user.id,
    )


@router.get(
    "/{media_id}",
    response_model=MediaResponse,
)
def get_media(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MediaService.get_media(
        db=db,
        media_id=media_id,
    )


@router.get(
    "/message/{message_id}",
    response_model=list[MediaResponse],
)
def list_message_media(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MediaService.list_media(
        db=db,
        message_id=message_id,
    )


@router.get(
    "/download/{media_id}",
)
def download_media(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    media = MediaService.get_media(
        db=db,
        media_id=media_id,
    )

    path = MediaService.download_path(
        db=db,
        media_id=media_id,
    )

    return FileResponse(
        path=path,
        filename=media.original_name,
        media_type=media.mime_type,
    )


@router.delete(
    "/{media_id}",
    response_model=DeleteMediaResponse,
)
def delete_media(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    MediaService.delete_media(
        db=db,
        media_id=media_id,
    )

    return DeleteMediaResponse(
        success=True,
        message="Media deleted successfully.",
    )