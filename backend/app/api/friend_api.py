from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.friend import FriendRequestCreate, FriendRequestResponse, FriendActionResponse, FriendListItem
from app.services.friend_service import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    remove_friend,
    get_friends,
)

router=APIRouter(prefix='/friends',tags=['Friends'])

@router.post('/request',response_model=FriendRequestResponse,status_code=status.HTTP_201_CREATED)
def request_friend(payload:FriendRequestCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    try:
        return send_friend_request(db,current_user.id,payload.addressee_id)
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))

@router.post('/accept/{friend_id}',response_model=FriendRequestResponse)
def accept(friend_id,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    try:
        return accept_friend_request(db,friend_id,current_user.id)
    except ValueError as e:
        # if not found or unauthorized, map to 404/403 appropriately
        msg = str(e)
        if 'not found' in msg.lower():
            raise HTTPException(status_code=404,detail=msg)
        else:
            raise HTTPException(status_code=403,detail=msg)

@router.post('/reject/{friend_id}',response_model=FriendRequestResponse)
def reject(friend_id,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    try:
        return reject_friend_request(db,friend_id,current_user.id)
    except ValueError as e:
        msg = str(e)
        if 'not found' in msg.lower():
            raise HTTPException(status_code=404,detail=msg)
        else:
            raise HTTPException(status_code=403,detail=msg)

@router.delete('/{friend_id}',response_model=FriendActionResponse)
def delete(friend_id,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    try:
        remove_friend(db,friend_id,current_user.id)
        return {'success':True,'message':'Friend removed.'}
    except ValueError as e:
        msg = str(e)
        if 'not found' in msg.lower():
            raise HTTPException(status_code=404,detail=msg)
        else:
            raise HTTPException(status_code=403,detail=msg)

@router.get('',response_model=list[FriendListItem])
def list_friends(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return get_friends(db,current_user.id)
