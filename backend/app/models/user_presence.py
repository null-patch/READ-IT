import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.database import Base


class UserPresence(Base):
    __tablename__ = "user_presence"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    online = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
