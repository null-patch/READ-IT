from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User

from app.schemas.friend import (
    FriendRequestCreate,
    FriendRequestResponse,
    FriendActionResponse,
)

from app.services.friend import FriendService

router = APIRouter(
    prefix="/friends",
    tags=["Friends"],
)


@router.post(
    "/request",
    response_model=FriendRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_friend_request(
    payload: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FriendService.send_request(
        db=db,
        requester_id=current_user.id,
        addressee_id=payload.addressee_id,
    )


@router.post(
    "/accept/{request_id}",
    response_model=FriendRequestResponse,
)
def accept_friend_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FriendService.accept_request(
        db=db,
        request_id=request_id,
        user_id=current_user.id,
    )


@router.post(
    "/reject/{request_id}",
    response_model=FriendRequestResponse,
)
def reject_friend_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FriendService.reject_request(
        db=db,
        request_id=request_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{friend_id}",
    response_model=FriendActionResponse,
)
def remove_friend(
    friend_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    FriendService.remove_friend(
        db=db,
        user_id=current_user.id,
        friend_id=friend_id,
    )

    return FriendActionResponse(
        success=True,
        message="Friend removed successfully.",
    )


@router.get(
    "/",
    response_model=list[FriendRequestResponse],
)
def list_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FriendService.get_friends(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/pending",
    response_model=list[FriendRequestResponse],
)
def pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FriendService.get_pending_requests(
        db=db,
        user_id=current_user.id,
    )