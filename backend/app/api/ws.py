from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.conversation_member import ConversationMember
from app.models.user import User
from app.services.message_service import send_message
from app.services.websocket_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint that:
    - authenticates using the same JWT used by HTTP endpoints (query param 'token')
    - verifies the connecting user is a member of the conversation
    - persists messages before broadcasting
    - broadcasts typing/read events
    Expected message shapes (JSON):
      { "type": "message", "message_type": "text", "content": "hello" }
      { "type": "typing", "status": true }
      { "type": "read", "message_id": "<uuid>" }
    """
    # Extract token from query params
    token: str | None = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4002)
        return

    sub = payload.get("sub")
    if not sub:
        await websocket.close(code=4003)
        return

    try:
        user_id = UUID(sub)
    except Exception:
        await websocket.close(code=4004)
        return

    # Acquire DB session from get_db generator safely
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Ensure user exists
        user: User = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4005)
            return

        # Ensure user is a member of the conversation
        membership = (
            db.query(ConversationMember)
            .filter(
                ConversationMember.conversation_id == conversation_id,
                ConversationMember.user_id == user_id,
            )
            .first()
        )
        if not membership:
            await websocket.close(code=4006)
            return

        # Register connection
        await manager.connect(conversation_id, websocket, str(user_id))

        # Mark presence (best-effort)
        try:
            user.status = "online"
            db.add(user)
            db.commit()
        except Exception:
            db.rollback()

        try:
            while True:
                data = await websocket.receive_json()

                if not isinstance(data, dict) or "type" not in data:
                    # ignore malformed messages
                    continue

                typ = data["type"]

                if typ == "message":
                    # Persist the message first
                    message_type = data.get("message_type", "text")
                    content = data.get("content")
                    try:
                        msg = send_message(db, conversation_id, user_id, message_type, content)
                    except ValueError as e:
                        # send error back to sender only
                        await websocket.send_json({"event": "error", "message": str(e)})
                        continue

                    payload = {
                        "event": "message",
                        "message": {
                            "id": str(msg.id),
                            "conversation_id": str(msg.conversation_id),
                            "sender_id": str(msg.sender_id) if msg.sender_id else None,
                            "message_type": msg.message_type,
                            "content": msg.content,
                            "created_at": msg.created_at.isoformat() if msg.created_at else None,
                        },
                    }
                    # broadcast to others (exclude sender connections)
                    await manager.send_to_conversation(conversation_id, payload, exclude_user_id=str(user_id))

                    # send ack to sender (optionally)
                    await websocket.send_json({"event": "sent", "message_id": str(msg.id)})

                elif typ == "typing":
                    status = data.get("status", True)
                    evt = {"event": "typing", "user_id": str(user_id), "status": bool(status)}
                    await manager.send_to_conversation(conversation_id, evt, exclude_user_id=str(user_id))

                elif typ == "read":
                    # Broadcast read receipt. Persisting read receipts requires DB schema changes.
                    message_id = data.get("message_id")
                    evt = {"event": "read", "user_id": str(user_id), "message_id": message_id}
                    await manager.send_to_conversation(conversation_id, evt, exclude_user_id=str(user_id))

                else:
                    # Unknown event types are ignored
                    continue

        except WebSocketDisconnect:
            # client disconnected
            manager.disconnect(conversation_id, websocket)

    finally:
        # mark offline (best-effort) and close DB generator
        try:
            user.status = "offline"
            db.add(user)
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        try:
            db_gen.close()
        except Exception:
            pass