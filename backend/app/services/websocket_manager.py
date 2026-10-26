from typing import Any

from fastapi import WebSocket


# active_connections maps conversation_id -> list[{"ws": WebSocket, "user_id": str}]
class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[dict[str, Any]]] = {}

    async def connect(self, conversation_id: str, websocket: WebSocket, user_id: str) -> None:
        """
        Accept and register a websocket connection for a conversation and user.
        """
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        self.active_connections[conversation_id].append({"ws": websocket, "user_id": str(user_id)})

    def disconnect(self, conversation_id: str, websocket: WebSocket) -> None:
        """
        Remove connection from registry. If no connections remain for a conversation, delete key.
        """
        if conversation_id not in self.active_connections:
            return

        to_remove = None
        for entry in self.active_connections[conversation_id]:
            if entry["ws"] is websocket:
                to_remove = entry
                break

        if to_remove:
            self.active_connections[conversation_id].remove(to_remove)

        if len(self.active_connections.get(conversation_id, [])) == 0:
            del self.active_connections[conversation_id]

    async def send_to_conversation(
        self, conversation_id: str, message: dict, exclude_user_id: str | None = None
    ) -> None:
        """
        Send a message dict to all websockets in a conversation, optionally excluding connections
        that belong to exclude_user_id.
        """
        if conversation_id not in self.active_connections:
            return

        dead_connections: list[dict[str, Any]] = []

        for entry in list(self.active_connections[conversation_id]):
            ws = entry["ws"]
            uid = entry["user_id"]
            if exclude_user_id is not None and str(uid) == str(exclude_user_id):
                # Skip sending to the excluded user
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(entry)

        for dead in dead_connections:
            self.disconnect(conversation_id, dead["ws"])


manager = ConnectionManager()