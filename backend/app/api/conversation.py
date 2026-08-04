from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)

from app.services.conversation_service import (
    create_conversation,
    get_all_conversations,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/",
    response_model=ConversationResponse,
)
def new_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
):
    return create_conversation(
        db,
        conversation,
    )


@router.get(
    "/",
    response_model=list[ConversationResponse],
)
def conversations(
    db: Session = Depends(get_db),
):
    return get_all_conversations(db)
