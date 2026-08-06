import mimetypes
import shutil
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.media import Media, MediaType
from app.models.message import Message

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


class MediaService:

    @staticmethod
    def upload(
        db: Session,
        file: UploadFile,
        message_id: UUID,
        uploader_id: UUID,
    ) -> Media:

        message = (
            db.query(Message)
            .filter(Message.id == message_id)
            .first()
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found.",
            )

        data = file.file.read()

        if len(data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large.",
            )

        mime = (
            file.content_type
            or mimetypes.guess_type(file.filename)[0]
            or "application/octet-stream"
        )

        if mime.startswith("image/"):
            media_type = MediaType.IMAGE
        elif mime.startswith("video/"):
            media_type = MediaType.VIDEO
        elif mime.startswith("audio/"):
            media_type = MediaType.AUDIO
        else:
            media_type = MediaType.FILE

        extension = Path(file.filename).suffix

        stored_name = f"{uuid.uuid4()}{extension}"

        path = UPLOAD_DIR / stored_name

        with open(path, "wb") as output:
            output.write(data)

        media = Media(
            message_id=message_id,
            uploader_id=uploader_id,
            media_type=media_type,
            original_name=file.filename,
            stored_name=stored_name,
            mime_type=mime,
            file_size=len(data),
            file_path=str(path),
        )

        db.add(media)
        db.commit()
        db.refresh(media)

        return media

    @staticmethod
    def list_media(
        db: Session,
        message_id: UUID,
    ):
        return (
            db.query(Media)
            .filter(
                Media.message_id == message_id,
            )
            .all()
        )

    @staticmethod
    def get_media(
        db: Session,
        media_id: UUID,
    ) -> Media:

        media = (
            db.query(Media)
            .filter(Media.id == media_id)
            .first()
        )

        if not media:
            raise HTTPException(
                status_code=404,
                detail="Media not found.",
            )

        return media

    @staticmethod
    def delete_media(
        db: Session,
        media_id: UUID,
    ):

        media = MediaService.get_media(
            db,
            media_id,
        )

        path = Path(media.file_path)

        if path.exists():
            path.unlink()

        db.delete(media)
        db.commit()

    @staticmethod
    def download_path(
        db: Session,
        media_id: UUID,
    ) -> Path:

        media = MediaService.get_media(
            db,
            media_id,
        )

        path = Path(media.file_path)

        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail="File missing.",
            )

        return path
