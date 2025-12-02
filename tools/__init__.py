"""
SPECTRE Tools Package

MCP tool implementations for world generation and manipulation.
"""

from .world_tools import *
from .region_tools import *
from .poi_tools import *
from .lore_tools import *

__all__ = [
    # World tools
    'create_world',
    'get_world',
    'get_statistics',

    # Region tools
    'get_region',
    'name_region',
    'describe_region',
    'batch_name_regions',

    # POI tools
    'list_pois',
    'create_poi',
    'update_poi',
    'detail_poi',

    # Lore tools
    'generate_world_lore',
    'add_historical_event'
]

# Tool registry
TOOL_REGISTRY = {
    'world': {
        'create_world': 'Create a new procedural world',
        'get_world': 'Retrieve existing world data',
        'get_statistics': 'Get world statistics'
    },
    'region': {
        'get_region': 'Get region details',
        'name_region': 'Name a specific region',
        'describe_region': 'Generate region description',
        'batch_name_regions': 'Name multiple regions'
    },
    'poi': {
        'list_pois': 'List all points of interest',
        'create_poi': 'Create new POI',
        'update_poi': 'Update existing POI',
        'detail_poi': 'Generate detailed POI content'
    },
    'lore': {
        'generate_world_lore': 'Create world mythology',
        'add_historical_event': 'Add timeline event'
    }
}