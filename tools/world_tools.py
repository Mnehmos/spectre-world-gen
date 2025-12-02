"""
SPECTRE Tools - World Management Tools

MCP tools for world creation and management.
"""

from typing import Dict, Any, Optional
from server.world_engine import WorldEngine
from server.events import EventBroadcaster

# Initialize engine and broadcaster
engine = WorldEngine()
broadcaster = EventBroadcaster(None)  # Will be initialized by MCP handler

def create_world(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new procedural world.

    Args:
        args: Tool arguments including width, height, seed, island_mode

    Returns:
        World creation result
    """
    width = args.get('width', 64)
    height = args.get('height', 64)
    seed = args.get('seed')
    island_mode = args.get('island_mode', True)

    world_data = engine.create_world(width, height, seed, island_mode)

    # Broadcast event
    broadcaster.emit("world_created", {
        "world_id": world_data["id"],
        "width": width,
        "height": height,
        "seed": world_data["seed"],
        "island_mode": island_mode
    })

    return {
        "world_id": world_data["id"],
        "width": width,
        "height": height,
        "seed": world_data["seed"],
        "island_mode": island_mode,
        "message": "World created successfully"
    }

def get_world(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get existing world data.

    Args:
        args: Tool arguments including world_id

    Returns:
        World data or error
    """
    world_id = args.get('world_id')
    if not world_id:
        return {"error": "world_id is required"}

    world_data = engine.get_world(world_id)

    if not world_data:
        return {"error": "World not found"}

    return {
        "world": world_data,
        "message": "World retrieved successfully"
    }

def get_statistics(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get world statistics.

    Args:
        args: Tool arguments including world_id

    Returns:
        Statistics data or error
    """
    world_id = args.get('world_id')
    if not world_id:
        return {"error": "world_id is required"}

    stats = engine.get_statistics(world_id)

    if not stats:
        return {"error": "World not found"}

    # Broadcast statistics update
    broadcaster.emit("statistics_updated", {
        "world_id": world_id,
        "statistics": stats
    })

    return {
        "statistics": stats,
        "message": "Statistics retrieved successfully"
    }

# Tool definitions for MCP protocol
WORLD_TOOLS = {
    "create_world": {
        "description": "Create a new procedural world",
        "parameters": {
            "width": {"type": "integer", "default": 64},
            "height": {"type": "integer", "default": 64},
            "seed": {"type": "string", "optional": True},
            "island_mode": {"type": "boolean", "default": True}
        },
        "returns": {
            "world_id": "string",
            "width": "integer",
            "height": "integer",
            "seed": "string",
            "island_mode": "boolean"
        }
    },
    "get_world": {
        "description": "Retrieve existing world data",
        "parameters": {
            "world_id": {"type": "string", "required": True}
        },
        "returns": {
            "world": "object",
            "message": "string"
        }
    },
    "get_statistics": {
        "description": "Get world statistics",
        "parameters": {
            "world_id": {"type": "string", "required": True}
        },
        "returns": {
            "statistics": "object",
            "message": "string"
        }
    }
}