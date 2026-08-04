import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    username = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    display_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    avatar_url = Column(
        Text,
        nullable=True
    )

    bio = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="offline"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
