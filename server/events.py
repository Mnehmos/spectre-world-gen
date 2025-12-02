"""
SPECTRE World Generation - Event Broadcasting Module

Handles WebSocket event broadcasting and cross-thread communication.
"""

import queue
import json
import threading
from typing import Dict, Any, Optional

class EventBroadcaster:
    """
    Manages event broadcasting to WebSocket clients.
    """

    def __init__(self, event_queue: queue.Queue):
        self.event_queue = event_queue
        self.event_counter = 0
        self.lock = threading.Lock()

    def emit(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event to be broadcast to clients.

        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        with self.lock:
            self.event_counter += 1

            event = {
                "id": self.event_counter,
                "type": event_type,
                "timestamp": self._get_current_timestamp(),
                "data": data
            }

            # Put event in queue for WebSocket broadcasting
            self.event_queue.put(event)

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def broadcast_system_message(self, message: str, level: str = "info"):
        """
        Broadcast a system-level message.

        Args:
            message: Message text
            level: Message level (info, warning, error)
        """
        self.emit("system_message", {
            "message": message,
            "level": level
        })

    def broadcast_world_event(self, world_id: str, event_type: str, data: Dict[str, Any]):
        """
        Broadcast a world-specific event.

        Args:
            world_id: World identifier
            event_type: Event type
            data: Event data
        """
        data["world_id"] = world_id
        self.emit(f"world_{event_type}", data)

    def log_event(self, category: str, message: str, data: Optional[Dict] = None):
        """
        Log an event for debugging/development.

        Args:
            category: Event category
            message: Event message
            data: Additional data
        """
        self.emit("log_event", {
            "category": category,
            "message": message,
            "data": data or {}
        })

# Global event broadcaster instance
global_broadcaster = None

def initialize_broadcaster(event_queue: queue.Queue):
    """
    Initialize the global broadcaster instance.

    Args:
        event_queue: Event queue for cross-thread communication
    """
    global global_broadcaster
    global_broadcaster = EventBroadcaster(event_queue)

def get_broadcaster() -> EventBroadcaster:
    """
    Get the global broadcaster instance.

    Returns:
        EventBroadcaster instance
    """
    if global_broadcaster is None:
        raise RuntimeError("Event broadcaster not initialized")
    return global_broadcaster