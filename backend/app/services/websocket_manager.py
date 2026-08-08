import asyncio
from fastapi import WebSocket
from typing import Dict, List, Any, Optional

# active_connections maps conversation_id -> list[{"ws": WebSocket, "user_id": str}]
class ConnectionManager:
    def __init__(self) -> None:
        # Map conversation_id -> list of connection entries
        self.active_connections: Dict[str, List[Dict[str, Any]]] = {}
        # Per-conversation locks to guard connection lists
        self._locks: Dict[str, asyncio.Lock] = {}
        # Manager-level lock to guard creation/deletion of conversation entries and locks
        self._manager_lock = asyncio.Lock()

    async def connect(self, conversation_id: str, websocket: WebSocket, user_id: str) -> None:
        """
        Accept and register a websocket connection for a conversation and user.
        """
        await websocket.accept()

        # Ensure the conversation list and lock exist atomically
        async with self._manager_lock:
            if conversation_id not in self.active_connections:
                self.active_connections[conversation_id] = []
                self._locks[conversation_id] = asyncio.Lock()
            conv_lock = self._locks[conversation_id]

        # Append under the conversation lock
        async with conv_lock:
            self.active_connections[conversation_id].append({"ws": websocket, "user_id": str(user_id)})

    async def disconnect(self, conversation_id: str, websocket: WebSocket) -> None:
        """
        Remove connection from registry. If no connections remain for a conversation, delete key.
        """
        async with self._manager_lock:
            if conversation_id not in self.active_connections:
                return
            conv_lock = self._locks.get(conversation_id)

        if conv_lock is None:
            return

        async with conv_lock:
            to_remove = None
            for entry in self.active_connections.get(conversation_id, []):
                if entry["ws"] is websocket:
                    to_remove = entry
                    break

            if to_remove:
                self.active_connections[conversation_id].remove(to_remove)

            # If list is empty, remove the conversation entry and its lock
            if not self.active_connections.get(conversation_id):
                # acquire manager lock to modify top-level maps
                async with self._manager_lock:
                    # double-check under manager lock
                    if conversation_id in self.active_connections and not self.active_connections[conversation_id]:
                        del self.active_connections[conversation_id]
                        # cancel and remove the lock
                        lock = self._locks.pop(conversation_id, None)
                        # No direct way to cancel an asyncio.Lock; leaving cleanup to GC

    async def send_to_conversation(
        self, conversation_id: str, message: dict, exclude_user_id: Optional[str] = None
    ) -> None:
        """
        Send a message dict to all websockets in a conversation, optionally excluding connections
        that belong to exclude_user_id.
        """
        # Snapshot connections under the conversation lock to avoid holding the lock while sending
        async with self._manager_lock:
            if conversation_id not in self.active_connections:
                return
            conv_lock = self._locks.get(conversation_id)

        if conv_lock is None:
            return

        async with conv_lock:
            connections_snapshot = list(self.active_connections.get(conversation_id, []))

        dead_connections: List[Dict[str, Any]] = []

        for entry in connections_snapshot:
            ws = entry["ws"]
            uid = entry.get("user_id")
            if exclude_user_id is not None and str(uid) == str(exclude_user_id):
                # Skip sending to the excluded user
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(entry)

        if not dead_connections:
            return

        # Remove dead connections under the conversation lock
        async with conv_lock:
            for dead in dead_connections:
                if dead in self.active_connections.get(conversation_id, []):
                    self.active_connections[conversation_id].remove(dead)

            # If list is empty, cleanup the conversation entry and its lock
            if not self.active_connections.get(conversation_id):
                async with self._manager_lock:
                    if conversation_id in self.active_connections and not self.active_connections[conversation_id]:
                        del self.active_connections[conversation_id]
                        self._locks.pop(conversation_id, None)


manager = ConnectionManager()
