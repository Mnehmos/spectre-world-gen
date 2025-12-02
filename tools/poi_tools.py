
"""
SPECTRE Tools - POI Management Tools

MCP tools for point of interest creation and management.
"""

from typing import Dict, Any, List
from server.world_engine import WorldEngine
from server.events import EventBroadcaster

# Initialize engine and broadcaster
engine = WorldEngine()
broadcaster = EventBroadcaster(None)  # Will be initialized by MCP handler

def list_pois(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all points of interest in a world.

    Args:
        args: Tool arguments including world_id

    Returns:
        List of POIs
    """
    world_id = args.get('world_id')
    if not world_id:
        return {"error": "world_id is required"}

    pois = engine.list_pois(world_id)

    return {
        "pois": pois,
        "count": len(pois),
        "message": "POIs listed successfully"
    }

def create_poi(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new point of interest.

    Args:
        args: Tool arguments including world_id, poi_type, x, y, name

    Returns:
        Created POI data
    """
    world_id = args.get('world_id')
    poi_type = args.get('poi_type', 'settlement')
    x = args.get('x')
    y = args.get('y')
    name = args.get('name')

    if world_id is None or x is None or y is None:
        return {"error": "Missing required parameters"}

    poi = engine.create_poi(world_id, poi_type, x, y, name)

    # Broadcast POI creation
    broadcaster.emit("poi_created", {
        "id": poi["id"],
        "name": poi["name"],
        "type": poi["type"],
        "x": x,
        "y": y,
        "world_id": world_id
    })

    return {
        "poi": poi,
        "message": "POI created successfully"
    }

def update_poi(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing POI.

    Args:
        args: Tool arguments including world_id, poi_id, updates

    Returns:
        Updated POI data
    """
    world_id = args.get('world_id')
    poi_id = args.get('poi_id')
    updates = args.get('updates', {})

    if world_id is None or poi_id is None:
        return {"error": "Missing required parameters"}

    poi = engine.update_poi(world_id, poi_id, updates)

    # Broadcast POI update
    broadcaster.emit("poi_updated", {
        "id": poi_id,
        "updates": updates,
        "world_id": world_id
    })

    return {
        "poi": poi,
        "message": "POI updated successfully"
    }

def detail_poi(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate detailed content for a POI.

    Args:
        args: Tool arguments including world_id, poi_id, detail_level

    Returns:
        Detailed POI data
    """
    world_id = args.get('world_id')
    poi_id = args.get('poi_id')
    detail_level = args.get('detail_level', 'medium')

    if world_id is None or poi_id is None:
        return {"error": "Missing required parameters"}

    poi = engine.detail_poi(world_id, poi_id, detail_level)

    # Broadcast POI detailing
    broadcaster.emit("poi_detailed", {
        "id": poi_id,
        "name": poi["name"],
        "npcs": poi.get("npcs", []),
        "rumors": poi.get("rumors", []),
        "secrets": poi.get("secrets", []),
        "world_id": world_id
    })

    return {
        "poi": poi,
        "message": "POI detailed successfully"
    }

# Tool definitions for MCP protocol
POI_TOOLS = {
    "list_pois": {
        "description": "List all points of interest",
        "parameters": {
            "world_id": {"type": "string", "required": True}
        },
        "returns": {
            "pois": "array",
            "count": "integer",
            "message": "string"
        }
    },
    "create_poi": {
        "description": "Create new POI",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "poi_type": {"type": "string", "default": "settlement"},
            "x": {"type": "integer", "required": True},
            "y": {"type": "integer", "required": True},
            "name": {"type": "string", "optional": True}
        },
        "returns": {
            "poi": "object",
            "message": "string"
        }
    },
    "update_poi": {
        "description": "Update existing POI",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "poi_id": {"type": "string", "required": True},
            "updates": {"type": "object", "required": True}
        },
        "returns": {
            "poi": "object",
            "message": "string"
        }
    },
    "detail_poi": {
        "description": "Generate detailed POI content",
