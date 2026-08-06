from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.message_read import MessageRead
from app.models.conversation_member import ConversationMember


class MessageReadService:

    @staticmethod
    def mark_as_read(
        db: Session,
        message_id: UUID,
        user_id: UUID,
    ) -> MessageRead:

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

        member = (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == message.conversation_id,
                ConversationMember.user_id == user_id,
            )
            .first()
        )

        if not member:
            raise HTTPException(
                status_code=403,
                detail="Access denied.",
            )

        existing = (
            db.query(MessageRead)
            .filter(
                MessageRead.message_id == message_id,
                MessageRead.user_id == user_id,
            )
            .first()
        )

        if existing:
            return existing

        receipt = MessageRead(
            message_id=message_id,
            user_id=user_id,
        )

        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        return receipt

    @staticmethod
    def get_readers(
        db: Session,
        message_id: UUID,
    ):

        return (
            db.query(MessageRead)
            .filter(
                MessageRead.message_id == message_id,
            )
            .all()
        )

    @staticmethod
    def has_read(
        db: Session,
        message_id: UUID,
        user_id: UUID,
    ) -> bool:

        return (
            db.query(MessageRead)
            .filter(
                MessageRead.message_id == message_id,
                MessageRead.user_id == user_id,
            )
            .first()
            is not None
        )

    @staticmethod
    def unread_count(
        db: Session,
        message_id: UUID,
        conversation_id: UUID,
    ) -> int:

        members = (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == conversation_id,
            )
            .count()
        )

        reads = (
            db.query(MessageRead)
            .filter(
                MessageRead.message_id == message_id,
            )
            .count()
        )

        return max(members - reads, 0)
