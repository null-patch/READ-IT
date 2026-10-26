import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=True,
    )

    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    message_type = Column(
        String(20),
        nullable=True,
        default="text",
    )

    content = Column(
        Text,
        nullable=True,
    )

    edited = Column(
        Boolean,
        nullable=True,
        default=False,
    )

    deleted = Column(
        Boolean,
        nullable=True,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=True,
    )