from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user import UserCreate
from app.schemas.user import UserResponse

from app.schemas.token import Token

from app.services.user_service import (
    create_user,
    get_user_by_username,
    get_user_by_email,
)

from app.core.security import (
    verify_password,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=409,
            detail="Username already exists."
        )

    if user.email and get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=409,
            detail="Email already exists."
        )

    return create_user(db, user)


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = get_user_by_username(
        db,
        form_data.username,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    if not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
