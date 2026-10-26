<<<<<<< HEAD
=======
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
>>>>>>> 167c13c71ce4a67603e4657a8c6d2a8dbbd53845

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.friend import Friend, FriendStatus
from app.models.message import Message


def send_message(
    db: Session,
    conversation_id,
    sender_id,
    message_type: str = "text",
    content: str | None = None,
) -> Message:
    """
    Persist a message in the given conversation.

    For private conversations, enforce that the sender is accepted friends with the other member.
    Returns the persisted Message ORM instance (committed and refreshed).
    Raises ValueError on bad input or authorization errors.
    """
    # Normalize IDs to UUID objects for accurate DB comparisons
    try:
        conv_uuid = UUID(str(conversation_id))
    except Exception:
        raise ValueError("Invalid conversation id.")

    try:
        sender_uuid = UUID(str(sender_id))
    except Exception:
        raise ValueError("Invalid sender id.")

    # Ensure conversation exists
    conv: Conversation = (
        db.query(Conversation).filter(Conversation.id == conv_uuid).first()
    )
    if not conv:
        raise ValueError("Conversation not found.")

    # Ensure sender is a member of conversation
    membership = (
        db.query(ConversationMember)
        .filter(
            ConversationMember.conversation_id == conv_uuid,
            ConversationMember.user_id == sender_uuid,
        )
        .first()
    )
    if not membership:
        raise ValueError("Sender is not a member of the conversation.")

    # For private conversations, enforce friendship
    if conv.type == "private":
        # Find other members in the conversation (all except sender)
        other_members = (
            db.query(ConversationMember.user_id)
            .filter(
                ConversationMember.conversation_id == conv_uuid,
                ConversationMember.user_id != sender_uuid,
            )
            .all()
        )
        # If there are no other members (shouldn't happen) -> disallow
        if not other_members:
            raise ValueError("Private conversation has no other participant.")

        # For each other member ensure an ACCEPTED friendship exists with sender
        for (other_id,) in other_members:
            friend = (
                db.query(Friend)
                .filter(
                    or_(
                        (Friend.requester_id == sender_uuid) & (Friend.addressee_id == other_id),
                        (Friend.requester_id == other_id) & (Friend.addressee_id == sender_uuid),
                    ),
                    Friend.status == FriendStatus.ACCEPTED,
                )
                .first()
            )
            if not friend:
                raise ValueError("You can only message accepted friends in private conversations.")

    # Persist message
    msg = Message(
        conversation_id=conv_uuid,
        sender_id=sender_uuid,
        message_type=message_type,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
