from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}
        self.conversation_connections: dict[
            UUID,
            set[UUID],
        ] = defaultdict(set)

    async def connect(
        self,
        websocket: WebSocket,
        user_id: UUID,
    ):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(
        self,
        user_id: UUID,
    ):
        self.active_connections.pop(user_id, None)

        for users in self.conversation_connections.values():
            users.discard(user_id)

    def join_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ):
        self.conversation_connections[
            conversation_id
        ].add(user_id)

    def leave_conversation(
        self,
        user_id: UUID,
        conversation_id: UUID,
    ):
        if conversation_id in self.conversation_connections:
            self.conversation_connections[
                conversation_id
            ].discard(user_id)

    async def send_personal_message(
        self,
        user_id: UUID,
        message: dict,
    ):
        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_json(message)

    async def broadcast_to_conversation(
        self,
        conversation_id: UUID,
        message: dict,
        exclude: UUID | None = None,
    ):
        for user_id in self.conversation_connections.get(
            conversation_id,
            set(),
        ):
            if exclude and user_id == exclude:
                continue

            websocket = self.active_connections.get(user_id)

            if websocket:
                await websocket.send_json(message)

    def is_online(
        self,
        user_id: UUID,
    ) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()
