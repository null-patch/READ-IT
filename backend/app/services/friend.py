from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.friend import Friend, FriendStatus


class FriendService:

    @staticmethod
    def send_request(
        db: Session,
        requester_id: UUID,
        addressee_id: UUID,
    ) -> Friend:

        if requester_id == addressee_id:
            raise HTTPException(
                status_code=400,
                detail="You cannot add yourself."
            )

        existing = (
            db.query(Friend)
            .filter(
                or_(
                    and_(
                        Friend.requester_id == requester_id,
                        Friend.addressee_id == addressee_id,
                    ),
                    and_(
                        Friend.requester_id == addressee_id,
                        Friend.addressee_id == requester_id,
                    ),
                )
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Friend request already exists."
            )

        friend = Friend(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=FriendStatus.PENDING,
        )

        db.add(friend)
        db.commit()
        db.refresh(friend)

        return friend

    @staticmethod
    def accept_request(
        db: Session,
        request_id: UUID,
        user_id: UUID,
    ) -> Friend:

        request = (
            db.query(Friend)
            .filter(
                Friend.id == request_id,
                Friend.addressee_id == user_id,
                Friend.status == FriendStatus.PENDING,
            )
            .first()
        )

        if not request:
            raise HTTPException(
                status_code=404,
                detail="Friend request not found."
            )

        request.status = FriendStatus.ACCEPTED

        db.commit()
        db.refresh(request)

        return request

    @staticmethod
    def reject_request(
        db: Session,
        request_id: UUID,
        user_id: UUID,
    ) -> Friend:

        request = (
            db.query(Friend)
            .filter(
                Friend.id == request_id,
                Friend.addressee_id == user_id,
                Friend.status == FriendStatus.PENDING,
            )
            .first()
        )

        if not request:
            raise HTTPException(
                status_code=404,
                detail="Friend request not found."
            )

        request.status = FriendStatus.REJECTED

        db.commit()
        db.refresh(request)

        return request

    @staticmethod
    def remove_friend(
        db: Session,
        user_id: UUID,
        friend_id: UUID,
    ) -> None:

        friendship = (
            db.query(Friend)
            .filter(
                Friend.status == FriendStatus.ACCEPTED,
                or_(
                    and_(
                        Friend.requester_id == user_id,
                        Friend.addressee_id == friend_id,
                    ),
                    and_(
                        Friend.requester_id == friend_id,
                        Friend.addressee_id == user_id,
                    ),
                ),
            )
            .first()
        )

        if not friendship:
            raise HTTPException(
                status_code=404,
                detail="Friendship not found."
            )

        db.delete(friendship)
        db.commit()

    @staticmethod
    def get_friends(
        db: Session,
        user_id: UUID,
    ):

        return (
            db.query(Friend)
            .filter(
                Friend.status == FriendStatus.ACCEPTED,
                or_(
                    Friend.requester_id == user_id,
                    Friend.addressee_id == user_id,
                ),
            )
            .all()
        )

    @staticmethod
    def get_pending_requests(
        db: Session,
        user_id: UUID,
    ):

        return (
            db.query(Friend)
            .filter(
                Friend.addressee_id == user_id,
                Friend.status == FriendStatus.PENDING,
            )
            .all()
        )
