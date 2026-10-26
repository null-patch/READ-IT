from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.conversation import (
    AddParticipantRequest,
    ConversationCreate,
    ConversationMemberResponse,
    ConversationResponse,
    RemoveParticipantRequest,
)
from app.services.conversation import ConversationService


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConversationService.create_conversation(
        db=db,
        creator_id=current_user.id,
        conversation_type=payload.type,
        title=payload.title,
        participant_ids=payload.participant_ids,
    )


@router.get(
    "/",
    response_model=list[ConversationResponse],
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConversationService.get_conversations(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConversationService.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )


@router.post(
    "/{conversation_id}/participants",
    response_model=ConversationMemberResponse,
)
def add_participant(
    conversation_id: UUID,
    payload: AddParticipantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConversationService.add_participant(
        db=db,
        conversation_id=conversation_id,
        user_id=payload.user_id,
        requester_id=current_user.id,
    )


@router.delete(
    "/{conversation_id}/participants",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_participant(
    conversation_id: UUID,
    payload: RemoveParticipantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ConversationService.remove_participant(
        db=db,
        conversation_id=conversation_id,
        user_id=payload.user_id,
        requester_id=current_user.id,
    )


@router.get(
    "/{conversation_id}/participants",
    response_model=list[ConversationMemberResponse],
)
def get_participants(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ConversationService.get_members(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )