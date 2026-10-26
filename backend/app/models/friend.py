import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class FriendStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Friend(Base):
    __tablename__ = "friends"

    __table_args__ = (
        UniqueConstraint(
            "requester_id",
            "addressee_id",
            name="uq_friend_request",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    requester_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    addressee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status = Column(
        Enum(
            FriendStatus,
            name="friend_status",
            native_enum=True,
        ),
        nullable=False,
        default=FriendStatus.PENDING,
        server_default=FriendStatus.PENDING.value,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    requester = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="sent_friend_requests",
    )

    addressee = relationship(
        "User",
        foreign_keys=[addressee_id],
        back_populates="received_friend_requests",
    )