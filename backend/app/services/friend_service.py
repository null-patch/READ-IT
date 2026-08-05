"""Friend service skeleton generated for current project.

NOTE:
This file provides the service API compatible with the current project.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.friend import Friend, FriendStatus
from app.models.user import User


def send_friend_request(db: Session, requester_id, addressee_id):
    if requester_id == addressee_id:
        raise ValueError("Cannot send a friend request to yourself.")

    if not db.query(User).filter(User.id == addressee_id).first():
        raise ValueError("User not found.")

    existing = db.query(Friend).filter(
        or_(
            (Friend.requester_id == requester_id) & (Friend.addressee_id == addressee_id),
            (Friend.requester_id == addressee_id) & (Friend.addressee_id == requester_id),
        )
    ).first()

    if existing:
        raise ValueError("Friend request already exists.")

    friend = Friend(
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=FriendStatus.PENDING,
    )
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend


def accept_friend_request(db: Session, friend_id):
    friend = db.query(Friend).filter(Friend.id == friend_id).first()
    if not friend:
        raise ValueError("Friend request not found.")
    friend.status = FriendStatus.ACCEPTED
    db.commit()
    db.refresh(friend)
    return friend


def reject_friend_request(db: Session, friend_id):
    friend = db.query(Friend).filter(Friend.id == friend_id).first()
    if not friend:
        raise ValueError("Friend request not found.")
    friend.status = FriendStatus.REJECTED
    db.commit()
    db.refresh(friend)
    return friend


def remove_friend(db: Session, friend_id):
    friend = db.query(Friend).filter(Friend.id == friend_id).first()
    if not friend:
        raise ValueError("Friend relationship not found.")
    db.delete(friend)
    db.commit()
    return True


def get_friends(db: Session, user_id):
    return db.query(Friend).filter(
        ((Friend.requester_id == user_id) | (Friend.addressee_id == user_id)),
        Friend.status == FriendStatus.ACCEPTED,
    ).all()
