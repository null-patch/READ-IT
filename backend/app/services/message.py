from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.conversation_member import ConversationMember
from app.models.message import Message


class MessageService:

    @staticmethod
    def send_message(
        db: Session,
        conversation_id: UUID,
        sender_id: UUID,
        content: str,
        message_type: str = "text",
    ) -> Message:

        member = (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == sender_id,
            )
            .first()
        )

        if not member:
            raise HTTPException(
                status_code=403,
                detail="Not a conversation member.",
            )

        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ):

        member = (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == user_id,
            )
            .first()
        )

        if not member:
            raise HTTPException(
                status_code=403,
                detail="Access denied.",
            )

        return (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation_id,
                Message.deleted == False,
            )
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def edit_message(
        db: Session,
        message_id: UUID,
        sender_id: UUID,
        content: str,
    ) -> Message:

        message = (
            db.query(Message)
            .filter(
                Message.id == message_id,
                Message.sender_id == sender_id,
                Message.deleted == False,
            )
            .first()
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found.",
            )

        message.content = content
        message.edited = True

        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def delete_message(
        db: Session,
        message_id: UUID,
        sender_id: UUID,
    ):

        message = (
            db.query(Message)
            .filter(
                Message.id == message_id,
                Message.sender_id == sender_id,
                Message.deleted == False,
            )
            .first()
        )

        if not message:
            raise HTTPException(
                status_code=404,
                detail="Message not found.",
            )

        message.deleted = True

        db.commit()

    @staticmethod
    def get_message(
        db: Session,
        message_id: UUID,
    ):

        return (
            db.query(Message)
            .filter(
                Message.id == message_id,
            )
            .first()
        )
