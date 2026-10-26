import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    type = Column(
        String(20),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=True,
    )

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=True,
    )