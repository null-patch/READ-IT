"""Friend service implementation with full business rules.

This updates the existing skeleton to:
- enforce authorization (only addressee can accept/reject)
- prevent self-requests and duplicate requests (both directions)
- create or reuse a private conversation on friend acceptance
- ensure transactional integrity
- return data structures compatible with API response models
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.friend import Friend, FriendStatus
from app.models.user import User
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.schemas.conversation import ConversationCreate
from app.services.conversation_service import create_conversation


def send_friend_request(db: Session, requester_id, addressee_id):
    """Send a friend request from requester_id to addressee_id.

    Raises ValueError on invalid operations.
    Returns the created Friend ORM instance.
    """
    if requester_id == addressee_id:
        raise ValueError("Cannot send a friend request to yourself.")

    if not db.query(User).filter(User.id == addressee_id).first():
        raise ValueError("User not found.")

    # Prevent any existing friend relationship or request in either direction
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


def accept_friend_request(db: Session, friend_id, current_user_id):
    """Accept a pending friend request.

    Only the addressee of the request may accept it. On acceptance this will
    create (or reuse) a private conversation for the two users.

    Returns the updated Friend ORM instance.
    """
    # Use a transaction to ensure friend status update + conversation creation are atomic
    with db.begin():
        friend = db.query(Friend).filter(Friend.id == friend_id).first()
        if not friend:
            raise ValueError("Friend request not found.")

        if friend.addressee_id != current_user_id:
            raise ValueError("Only the addressee can accept this friend request.")

        if friend.status == FriendStatus.ACCEPTED:
            # already accepted
            db.refresh(friend)
            return friend

        friend.status = FriendStatus.ACCEPTED
        db.add(friend)

        # Ensure there's a private conversation for this pair (unordered)
        user_a = friend.requester_id
        user_b = friend.addressee_id

        # Look for an existing private conversation that has exactly these two members
        conv_subq = (
            db.query(Conversation.id)
            .join(ConversationMember, Conversation.id == ConversationMember.conversation_id)
            .filter(
                Conversation.type == "private",
                ConversationMember.user_id.in_([user_a, user_b]),
            )
            .group_by(Conversation.id)
            .having(func.count(ConversationMember.user_id) == 2)
            .limit(1)
            .subquery()
        )

        conv = None
        if conv_subq is not None:
            conv_row = db.query(Conversation).filter(Conversation.id == conv_subq.c.id).first()
            if conv_row:
                conv = conv_row

        if not conv:
            # Create conversation using conversation service so behavior is centralized
            conv_payload = ConversationCreate(type="private", title=None, created_by=current_user_id)
            conv = create_conversation(db, conv_payload)

            # Add both members
            member_a = ConversationMember(conversation_id=conv.id, user_id=user_a)
            member_b = ConversationMember(conversation_id=conv.id, user_id=user_b)
            db.add_all([member_a, member_b])

    # transaction commits here
    db.refresh(friend)
    return friend


def reject_friend_request(db: Session, friend_id, current_user_id):
    """Reject a pending friend request.

    Only the addressee may reject. Returns the updated Friend ORM instance.
    """
    with db.begin():
        friend = db.query(Friend).filter(Friend.id == friend_id).first()
        if not friend:
            raise ValueError("Friend request not found.")

        if friend.addressee_id != current_user_id:
            raise ValueError("Only the addressee can reject this friend request.")

        friend.status = FriendStatus.REJECTED
        db.add(friend)

    db.refresh(friend)
    return friend


def remove_friend(db: Session, friend_id, current_user_id):
    """Remove a friend relationship.

    Only a participant of the friend relationship may remove it.
    Returns True on success.
    """
    with db.begin():
        friend = db.query(Friend).filter(Friend.id == friend_id).first()
        if not friend:
            raise ValueError("Friend relationship not found.")

        if current_user_id not in (friend.requester_id, friend.addressee_id):
            raise ValueError("Not authorized to remove this friendship.")

        db.delete(friend)

    return True


def get_friends(db: Session, user_id):
    """Return a list of friend list items for the given user.

    Each item contains the other user's public profile and the friendship status.
    """
    friends = (
        db.query(Friend)
        .filter(
            ((Friend.requester_id == user_id) | (Friend.addressee_id == user_id)),
            Friend.status == FriendStatus.ACCEPTED,
        )
        .all()
    )

    result = []
    for f in friends:
        other_id = f.addressee_id if f.requester_id == user_id else f.requester_id
        other_user = db.query(User).filter(User.id == other_id).first()
        if not other_user:
            # If user was deleted, skip
            continue
        item = {
            "id": other_user.id,
            "username": other_user.username,
            "display_name": other_user.display_name,
            "avatar_url": other_user.avatar_url,
            "bio": other_user.bio,
            "status": f.status.value if hasattr(f.status, "value") else str(f.status),
        }
        result.append(item)

    return result
