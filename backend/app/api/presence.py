from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.presence import PresenceService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/presence",
    tags=["Presence"],
)


@router.get("/{user_id}")
def get_presence(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    presence = PresenceService.get_presence(
        db=db,
        user_id=user_id,
    )

    if not presence:
        return {
            "user_id": str(user_id),
            "online": False,
            "last_seen": None,
        }

    return {
        "user_id": str(user_id),
        "online": presence.online,
        "last_seen": presence.last_seen,
    }


@router.get("/online/list")
def online_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = PresenceService.get_online_users(db)

    return [
        {
            "user_id": str(user.user_id),
            "online": user.online,
            "last_seen": user.last_seen,
        }
        for user in users
    ]
