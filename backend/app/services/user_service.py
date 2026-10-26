from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_id(
    db: Session,
    user_id: str,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_username(
    db: Session,
    username: str,
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
):
    if email is None:
        return None

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    user: UserCreate,
):

    db_user = User(
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user