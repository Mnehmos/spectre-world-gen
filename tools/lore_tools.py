"""
SPECTRE Tools - Lore Generation Tools

MCP tools for world mythology and history creation.
"""

from typing import Dict, Any, List
from server.world_engine import WorldEngine
from server.events import EventBroadcaster

# Initialize engine and broadcaster
engine = WorldEngine()
broadcaster = EventBroadcaster(None)  # Will be initialized by MCP handler

def generate_world_lore(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate world mythology and lore.

    Args:
        args: Tool arguments including world_id, lore_type, themes

    Returns:
        Generated lore data
    """
    world_id = args.get('world_id')
    lore_type = args.get('lore_type', 'creation_myth')
    themes = args.get('themes', [])

    if not world_id:
        return {"error": "world_id is required"}

    lore = engine.generate_world_lore(world_id, lore_type, themes)

    # Broadcast lore creation
    broadcaster.emit("lore_created", {
        "type": lore_type,
        "title": lore["title"],
        "content": lore["content"],
        "themes": themes,
        "world_id": world_id
    })

    return {
        "lore": lore,
        "message": "World lore generated successfully"
    }

def add_historical_event(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a historical event to world timeline.

    Args:
        args: Tool arguments including world_id, event_type, description, date

    Returns:
        Created event data
    """
    world_id = args.get('world_id')
    event_type = args.get('event_type', 'discovery')
    description = args.get('description')
    date = args.get('date')

    if not world_id or not description:
        return {"error": "world_id and description are required"}

    event = engine.add_historical_event(world_id, event_type, description, date)

    # Broadcast historical event
    broadcaster.emit("historical_event_added", {
        "type": event_type,
        "description": description,
        "date": event["date"],
        "world_id": world_id
    })

    return {
        "event": event,
        "message": "Historical event added successfully"
    }

# Tool definitions for MCP protocol
LORE_TOOLS = {
    "generate_world_lore": {
        "description": "Generate world mythology and lore",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "lore_type": {
                "type": "string",
                "default": "creation_myth",
                "enum": ["creation_myth", "historical_event", "legend"]
            },
            "themes": {
                "type": "array",
                "items": {"type": "string"},
                "default": []
            }
        },
        "returns": {
            "lore": "object",
            "message": "string"
        }
    },
    "add_historical_event": {
        "description": "Add event to world timeline",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "event_type": {"type": "string", "default": "discovery"},
            "description": {"type": "string", "required": True},
            "date": {"type": "string", "optional": True}
        },
        "returns": {
            "event": "object",
            "message": "string"
        }
    }
}