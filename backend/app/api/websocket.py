from uuid import UUID
import json

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi import status
from jose import JWTError
from jose import jwt

from app.core.config import settings
from app.websocket.manager import manager

router = APIRouter(tags=["WebSocket"])


def get_user_id(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise JWTError()

        return UUID(user_id)

    except JWTError:
        raise ValueError("Invalid token")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
        )
        return

    try:
        user_id = get_user_id(token)
    except ValueError:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
        )
        return

    await manager.connect(
        websocket,
        user_id,
    )

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            event = data.get("event")

            if event == "join":
                manager.join_conversation(
                    user_id,
                    UUID(data["conversation_id"]),
                )

            elif event == "leave":
                manager.leave_conversation(
                    user_id,
                    UUID(data["conversation_id"]),
                )

            elif event == "typing":
                await manager.broadcast_to_conversation(
                    UUID(data["conversation_id"]),
                    {
                        "event": "typing",
                        "user_id": str(user_id),
                    },
                    exclude=user_id,
                )

            elif event == "message":
                await manager.broadcast_to_conversation(
                    UUID(data["conversation_id"]),
                    {
                        "event": "message",
                        "conversation_id": data["conversation_id"],
                        "sender_id": str(user_id),
                        "content": data["content"],
                    },
                )

            elif event == "read":
                await manager.broadcast_to_conversation(
                    UUID(data["conversation_id"]),
                    {
                        "event": "read",
                        "conversation_id": data["conversation_id"],
                        "message_id": data["message_id"],
                        "user_id": str(user_id),
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(user_id)