import asyncio
import json
import logging
from typing import Dict, List, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class EventHub:
    """
    Real-Time WebSocket & Streaming Event Hub.
    Broadcasts live backend execution events to connected developer clients.
    """

    def __init__(self):
        # Maps session_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket client connected to session {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session {session_id}")

    async def broadcast_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Emits a live event to all connected clients for a session."""
        message = {
            "session_id": session_id,
            "event_type": event_type,
            "data": data
        }
        text_payload = json.dumps(message)
        
        connections = self.active_connections.get(session_id, [])
        for conn in list(connections):
            try:
                await conn.send_text(text_payload)
            except Exception as e:
                logger.warning(f"Failed to send event to client: {e}")
                self.disconnect(session_id, conn)

event_hub = EventHub()

