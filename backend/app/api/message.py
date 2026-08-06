from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db

from app.models.user import User

from app.schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
)

from app.services.message import MessageService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService.send_message(
        db=db,
        conversation_id=payload.conversation_id,
        sender_id=current_user.id,
        content=payload.content,
        message_type=payload.message_type,
    )


@router.get(
    "/{conversation_id}",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: UUID,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService.get_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{message_id}",
    response_model=MessageResponse,
)
def edit_message(
    message_id: UUID,
    payload: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService.edit_message(
        db=db,
        message_id=message_id,
        sender_id=current_user.id,
        content=payload.content,
    )


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    MessageService.delete_message(
        db=db,
        message_id=message_id,
        sender_id=current_user.id,
    )
