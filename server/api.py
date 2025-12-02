"""
SPECTRE World Generation - REST API Module

Provides HTTP endpoints for web UI interaction.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .world_engine import WorldEngine
from .database import DatabaseManager

# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize components
engine = WorldEngine()
database = DatabaseManager()

# Models
class WorldRequest(BaseModel):
    width: int = 64
    height: int = 64
    seed: Optional[str] = None
    island_mode: bool = True

class RegionRequest(BaseModel):
    world_id: str
    x: int
    y: int
    name: Optional[str] = None

class POIRequest(BaseModel):
    world_id: str
    poi_type: str
    x: int
    y: int
    name: Optional[str] = None

class LoreRequest(BaseModel):
    world_id: str
    lore_type: str
    themes: List[str] = []

# API Endpoints
@router.post("/worlds")
async def create_world(request: WorldRequest):
    """
    Create a new procedural world.
    """
    try:
        world_data = engine.create_world(
            width=request.width,
            height=request.height,
            seed=request.seed,
            island_mode=request.island_mode
        )

        # Save to database
        await database.save_world(world_data["id"], world_data)

        return {
            "status": "success",
            "world_id": world_data["id"],
            "message": "World created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world_id}")
async def get_world(world_id: str):
    """
    Get world data by ID.
    """
    try:
        # Try to get from memory first
        world_data = engine.get_world(world_id)

        if not world_data:
            # Load from database
            world_data = await database.load_world(world_id)

        if not world_data:
            raise HTTPException(status_code=404, detail="World not found")

        return {
            "status": "success",
            "world": world_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world_id}/regions/{x}/{y}")
async def get_region(world_id: str, x: int, y: int):
    """
    Get region details at specific coordinates.
    """
    try:
        region = engine.get_region(world_id, x, y)

        if not region:
            raise HTTPException(status_code=404, detail="Region not found")

        return {
            "status": "success",
            "region": region
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world_id}/regions/name")
async def name_region(request: RegionRequest):
    """
    Name a region.
    """
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="Name is required")

        region = engine.name_region(
            world_id=request.world_id,
            x=request.x,
            y=request.y,
            name=request.name
        )

        return {
            "status": "success",
            "region": region
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world_id}/regions/describe")
async def describe_region(request: RegionRequest):
    """
    Generate rich description for a region.
    """
    try:
        description = engine.describe_region(
            world_id=request.world_id,
            x=request.x,
            y=request.y
        )

        return {
            "status": "success",
            "description": description
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world_id}/pois")
async def list_pois(world_id: str):
    """
    List all points of interest in a world.
    """
    try:
        pois = engine.list_pois(world_id)

        return {
            "status": "success",
            "pois": pois,
            "count": len(pois)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world_id}/pois")
async def create_poi(request: POIRequest):
    """
    Create a new point of interest.
    """
    try:
        poi = engine.create_poi(
            world_id=request.world_id,
            poi_type=request.poi_type,
            x=request.x,
            y=request.y,
            name=request.name
        )

        # Save to database
        await database.save_poi(poi["id"], request.world_id, poi)

        return {
            "status": "success",
            "poi": poi
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world_id}/pois/{poi_id}")
async def get_poi(world_id: str, poi_id: str):
    """
    Get POI details.
    """
    try:
        # Try to get from memory first
        world_data = engine.get_world(world_id)
        poi = world_data["pois"].get(poi_id) if world_data else None

        if not poi:
            # Load from database
            poi = await database.load_poi(poi_id)

        if not poi:
            raise HTTPException(status_code=404, detail="POI not found")

        return {
            "status": "success",
            "poi": poi
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world_id}/pois/{poi_id}/detail")
async def detail_poi(world_id: str, poi_id: str, detail_level: str = "medium"):
    """
    Generate detailed content for a POI.
    """
    try:
        poi = engine.detail_poi(world_id, poi_id, detail_level)

        # Update in database
        await database.save_poi(poi_id, world_id, poi)

        return {
            "status": "success",
            "poi": poi
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worlds/{world_id}/lore")
async def generate_lore(request: LoreRequest):
    """
    Generate world lore.
    """
    try:
        lore = engine.generate_world_lore(
            world_id=request.world_id,
            lore_type=request.lore_type,
            themes=request.themes
        )

        # Save to database
        await database.save_lore(
            lore_id=lore["id"],
            world_id=request.world_id,
            lore_type=request.lore_type,
            title=lore["title"],
            content=lore["content"]
        )

        return {
            "status": "success",
            "lore": lore
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world_id}/lore")
async def get_lore(world_id: str, lore_type: Optional[str] = None):
    """
    Get world lore entries.
    """
    try:
        lore_entries = await database.get_lore(world_id, lore_type)

        return {
            "status": "success",
            "lore": lore_entries,
            "count": len(lore_entries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds/{world_id}/timeline")
async def get_timeline(world_id: str):
    """
    Get world timeline events.
    """
    try:
        timeline = await database.get_timeline(world_id)

        return {
            "status": "success",
            "timeline": timeline,
            "count": len(timeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worlds")
async def list_worlds():
    """
    List all available worlds.
    """
    try:
        world_ids = await database.list_worlds()

        return {
            "status": "success",
            "worlds": world_ids,
            "count": len(world_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/worlds/{world_id}")
async def delete_world(world_id: str):
    """
    Delete a world and all associated data.
    """
    try:
        # Delete from database
        await database.delete_world(world_id)

        # Remove from memory
        if world_id in engine.worlds:
            del engine.worlds[world_id]

        return {
            "status": "success",
            "message": "World deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "worlds_in_memory": len(engine.worlds)
    }

# Add router to main app (this will be called from main.py)
def add_router(app):
    """
    Add API router to FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.include_router(router)