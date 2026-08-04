from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.services.websocket_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
):

    await manager.connect(
        conversation_id,
        websocket,
    )

    try:

        while True:

            data = await websocket.receive_json()

            await manager.send_to_conversation(
                conversation_id,
                data,
            )

    except WebSocketDisconnect:

        manager.disconnect(
            conversation_id,
            websocket,
        )
