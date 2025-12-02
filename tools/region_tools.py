"""
SPECTRE Tools - Region Management Tools

MCP tools for region naming and description.
"""

from typing import Dict, Any, List
from server.world_engine import WorldEngine
from server.events import EventBroadcaster

# Initialize engine and broadcaster
engine = WorldEngine()
broadcaster = EventBroadcaster(None)  # Will be initialized by MCP handler

def get_region(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get region details at specific coordinates.

    Args:
        args: Tool arguments including world_id, x, y

    Returns:
        Region data or error
    """
    world_id = args.get('world_id')
    x = args.get('x')
    y = args.get('y')

    if world_id is None or x is None or y is None:
        return {"error": "Missing required parameters: world_id, x, y"}

    region = engine.get_region(world_id, x, y)

    if not region:
        return {"error": "Region not found"}

    return {
        "region": region,
        "message": "Region retrieved successfully"
    }

def name_region(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Name a specific region.

    Args:
        args: Tool arguments including world_id, x, y, name, style

    Returns:
        Named region data
    """
    world_id = args.get('world_id')
    x = args.get('x')
    y = args.get('y')
    name = args.get('name')
    style = args.get('style', 'fantasy')

    if world_id is None or x is None or y is None or name is None:
        return {"error": "Missing required parameters"}

    region = engine.name_region(world_id, x, y, name, style)

    # Broadcast region naming event
    broadcaster.emit("region_named", {
        "x": x,
        "y": y,
        "name": name,
        "biome": region["biome"],
        "world_id": world_id
    })

    return {
        "region": region,
        "message": "Region named successfully"
    }

def describe_region(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate rich description for a region.

    Args:
        args: Tool arguments including world_id, x, y

    Returns:
        Region description
    """
    world_id = args.get('world_id')
    x = args.get('x')
    y = args.get('y')

    if world_id is None or x is None or y is None:
        return {"error": "Missing required parameters"}

    description = engine.describe_region(world_id, x, y)

    # Broadcast region description event
    broadcaster.emit("region_described", {
        "x": x,
        "y": y,
        "description": description,
        "world_id": world_id
    })

    return {
        "description": description,
        "message": "Region described successfully"
    }

def batch_name_regions(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Name multiple regions at once.

    Args:
        args: Tool arguments including world_id, regions, style

    Returns:
        Batch naming results
    """
    world_id = args.get('world_id')
    regions = args.get('regions', [])
    style = args.get('style', 'fantasy')

    if not world_id or not regions:
        return {"error": "Missing required parameters: world_id, regions"}

    results = []
    for region_data in regions:
        x = region_data.get('x')
        y = region_data.get('y')
        name = region_data.get('name')

        if x is None or y is None or name is None:
            continue

        region = engine.name_region(world_id, x, y, name, style)
        results.append(region)

        # Broadcast each region naming
        broadcaster.emit("region_named", {
            "x": x,
            "y": y,
            "name": name,
            "biome": region["biome"],
            "world_id": world_id
        })

    return {
        "named_regions": len(results),
        "results": results,
        "message": "Batch region naming completed"
    }

# Tool definitions for MCP protocol
REGION_TOOLS = {
    "get_region": {
        "description": "Get region details at coordinates",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "x": {"type": "integer", "required": True},
            "y": {"type": "integer", "required": True}
        },
        "returns": {
            "region": "object",
            "message": "string"
        }
    },
    "name_region": {
        "description": "Name a specific region",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "x": {"type": "integer", "required": True},
            "y": {"type": "integer", "required": True},
            "name": {"type": "string", "required": True},
            "style": {"type": "string", "default": "fantasy"}
        },
        "returns": {
            "region": "object",
            "message": "string"
        }
    },
    "describe_region": {
        "description": "Generate region description",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "x": {"type": "integer", "required": True},
            "y": {"type": "integer", "required": True}
        },
        "returns": {
            "description": "string",
            "message": "string"
        }
    },
    "batch_name_regions": {
        "description": "Name multiple regions",
        "parameters": {
            "world_id": {"type": "string", "required": True},
            "regions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                },
                "required": True
            },
            "style": {"type": "string", "default": "fantasy"}
        },
        "returns": {
            "named_regions": "integer",
            "results": "array",
            "message": "string"
        }
    }
}