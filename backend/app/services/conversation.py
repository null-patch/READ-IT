from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember


class ConversationService:

    @staticmethod
    def create_conversation(
        db: Session,
        creator_id: UUID,
        conversation_type: str,
        title: str | None,
        participant_ids: list[UUID],
    ) -> Conversation:

        participants = list(set(participant_ids))

        if creator_id not in participants:
            participants.append(creator_id)

        conversation = Conversation(
            type=conversation_type,
            title=title,
            created_by=creator_id,
        )

        db.add(conversation)
        db.flush()

        for user_id in participants:
            db.add(
                ConversationMember(
                    conversation_id=conversation.id,
                    user_id=user_id,
                )
            )

        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversations(
        db: Session,
        user_id: UUID,
    ):

        return (
            db.query(Conversation)
            .join(
                ConversationMember,
                Conversation.id == ConversationMember.conversation_id,
            )
            .filter(
                ConversationMember.user_id == user_id,
            )
            .all()
        )

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ):

        conversation = (
            db.query(Conversation)
            .join(
                ConversationMember,
                Conversation.id == ConversationMember.conversation_id,
            )
            .filter(
                Conversation.id == conversation_id,
                ConversationMember.user_id == user_id,
            )
            .first()
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        return conversation

    @staticmethod
    def _verify_membership(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ) -> None:

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
                status_code=404,
                detail="Conversation not found.",
            )

    @staticmethod
    def add_participant(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        requester_id: UUID,
    ):

        ConversationService._verify_membership(
            db=db,
            conversation_id=conversation_id,
            user_id=requester_id,
        )

        exists = (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == user_id,
            )
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=409,
                detail="User already in conversation.",
            )

        member = ConversationMember(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        db.add(member)
        db.commit()
        db.refresh(member)

        return member

    @staticmethod
    def remove_participant(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
        requester_id: UUID,
    ):

        ConversationService._verify_membership(
            db=db,
            conversation_id=conversation_id,
            user_id=requester_id,
        )

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
                status_code=404,
                detail="Participant not found.",
            )

        db.delete(member)
        db.commit()

    @staticmethod
    def get_members(
        db: Session,
        conversation_id: UUID,
        user_id: UUID,
    ):

        ConversationService._verify_membership(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        return (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == conversation_id,
            )
            .all()
        )