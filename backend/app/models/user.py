import uuid

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    username = Column(
        String(30),
        unique=True,
        nullable=False,
    )

    display_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=True,
    )

    password_hash = Column(
        Text,
        nullable=False,
    )

    avatar_url = Column(
        Text,
        nullable=True,
    )

    bio = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(20),
        nullable=True,
        default="offline",
    )

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=True,
    )

    updated_at = Column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    sent_friend_requests = relationship(
        "Friend",
        foreign_keys="Friend.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan",
    )

    received_friend_requests = relationship(
        "Friend",
        foreign_keys="Friend.addressee_id",
        back_populates="addressee",
        cascade="all, delete-orphan",
    )