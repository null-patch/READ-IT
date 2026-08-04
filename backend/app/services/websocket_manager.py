from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(
        self,
        conversation_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        self.active_connections[conversation_id].append(websocket)

    def disconnect(
        self,
        conversation_id: str,
        websocket: WebSocket,
    ):

        if conversation_id not in self.active_connections:
            return

        if websocket in self.active_connections[conversation_id]:
            self.active_connections[conversation_id].remove(websocket)

        if len(self.active_connections[conversation_id]) == 0:
            del self.active_connections[conversation_id]

    async def send_to_conversation(
        self,
        conversation_id: str,
        message: dict,
    ):

        if conversation_id not in self.active_connections:
            return

        dead_connections = []

        for connection in self.active_connections[conversation_id]:

            try:

                await connection.send_json(message)

            except Exception:

                dead_connections.append(connection)

        for dead in dead_connections:

            self.disconnect(
                conversation_id,
                dead,
            )


manager = ConnectionManager()
