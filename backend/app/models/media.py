import uuid
import enum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    AUDIO = "audio"


class Media(Base):
    __tablename__ = "media"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    message_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "messages.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    uploader_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    media_type = Column(
        Enum(
            MediaType,
            name="media_type",
            native_enum=True,
        ),
        nullable=False,
    )

    original_name = Column(
        String(255),
        nullable=False,
    )

    stored_name = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    mime_type = Column(
        String(100),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
