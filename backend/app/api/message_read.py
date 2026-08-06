from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db

from app.models.user import User

from app.models.message_read import MessageRead

from app.services.message_read import MessageReadService

router = APIRouter(
    prefix="/messages",
    tags=["Read Receipts"],
)


@router.post(
    "/{message_id}/read",
    status_code=status.HTTP_201_CREATED,
)
def mark_as_read(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageReadService.mark_as_read(
        db=db,
        message_id=message_id,
        user_id=current_user.id,
    )


@router.get(
    "/{message_id}/readers",
    response_model=list[MessageRead],
)
def get_readers(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageReadService.get_readers(
        db=db,
        message_id=message_id,
    )


@router.get(
    "/{message_id}/has-read",
)
def has_read(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "read": MessageReadService.has_read(
            db=db,
            message_id=message_id,
            user_id=current_user.id,
        )
    }


@router.get(
    "/{conversation_id}/{message_id}/unread-count",
)
def unread_count(
    conversation_id: UUID,
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {
        "unread_count": MessageReadService.unread_count(
            db=db,
            conversation_id=conversation_id,
            message_id=message_id,
        )
    }
