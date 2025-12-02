"""
Event Broadcasting System

Handles WebSocket broadcasting and event management.
"""

import asyncio
import json
from fastapi import WebSocket
from typing import List, Dict, Any

class EventBroadcaster:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Add a new WebSocket connection"""
        await websocket.accept()
        self.connections.append(websocket)
        print(f"🔌 WebSocket connected. Total: {len(self.connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.connections.remove(websocket)
        print(f"🔌 WebSocket disconnected. Total: {len(self.connections)}")

    async def emit(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients"""
        if not self.connections:
            return

        message = json.dumps(event)
        disconnected = []

        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"🚨 WebSocket error: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.connections.remove(connection)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Convenience method for structured broadcasting"""
        event = {
            "type": event_type,
            "timestamp": self._get_timestamp(),
            **data
        }
        await self.emit(event)

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()

    async def send_error(self, error_message: str):
        """Send error message to all clients"""
        await self.emit({
            "type": "error",
            "message": error_message,
            "timestamp": self._get_timestamp()
        })

# Global broadcaster instance
broadcaster = EventBroadcaster()