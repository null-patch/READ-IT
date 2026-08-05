from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate


def create_conversation(
    db: Session,
    conversation: ConversationCreate,
):

    conv = Conversation(
        type=conversation.type,
        title=conversation.title,
        created_by=conversation.created_by,
    )

    db.add(conv)
    # NOTE: do not commit here so callers can control transactions
    db.flush()
    return conv


def get_conversation(
    db: Session,
    conversation_id,
):

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )


def get_all_conversations(db: Session):

    return (
        db.query(Conversation)
        .order_by(
            Conversation.created_at.desc()
        )
        .all()
    )
