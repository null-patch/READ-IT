from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql import func

from app.database.database import Base


class ConversationMember(Base):
    __tablename__ = "conversation_members"

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
