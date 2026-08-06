from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user_presence import UserPresence


class PresenceService:

    @staticmethod
    def connect(
        db: Session,
        user_id: UUID,
    ) -> UserPresence:

        presence = (
            db.query(UserPresence)
            .filter(UserPresence.user_id == user_id)
            .first()
        )

        if not presence:
            presence = UserPresence(
                user_id=user_id,
                online=True,
            )
            db.add(presence)
        else:
            presence.online = True

        db.commit()
        db.refresh(presence)

        return presence

    @staticmethod
    def disconnect(
        db: Session,
        user_id: UUID,
    ) -> UserPresence | None:

        presence = (
            db.query(UserPresence)
            .filter(UserPresence.user_id == user_id)
            .first()
        )

        if not presence:
            return None

        presence.online = False

        db.commit()
        db.refresh(presence)

        return presence

    @staticmethod
    def get_presence(
        db: Session,
        user_id: UUID,
    ) -> UserPresence | None:

        return (
            db.query(UserPresence)
            .filter(UserPresence.user_id == user_id)
            .first()
        )

    @staticmethod
    def is_online(
        db: Session,
        user_id: UUID,
    ) -> bool:

        presence = PresenceService.get_presence(
            db,
            user_id,
        )

        return bool(presence and presence.online)

    @staticmethod
    def get_online_users(
        db: Session,
    ):

        return (
            db.query(UserPresence)
            .filter(UserPresence.online == True)
            .all()
        )
