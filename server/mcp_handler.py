"""
SPECTRE World Generation - MCP Protocol Handler

Handles MCP protocol communication for Kilo Code integration.
"""

import json
import sys
import traceback
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.dirname(__file__))

from world_engine import WorldEngine
from events import EventBroadcaster
from database import DatabaseManager


def log_info(message: str) -> None:
    """Log message to stderr to avoid corrupting MCP stdout protocol."""
    print(message, file=sys.stderr, flush=True)

class MCPHandler:
    """
    Handles MCP protocol communication via stdio.
    """

    def __init__(self, world_engine: WorldEngine, event_broadcaster: EventBroadcaster, database: DatabaseManager):
        self.engine = world_engine
        self.broadcaster = event_broadcaster
        self.database = database
        self.running = False

        # Register tool implementations
        self.tools = {
            'create_world': self._tool_create_world,
            'get_world': self._tool_get_world,
            'get_statistics': self._tool_get_statistics,
            'get_region': self._tool_get_region,
            'name_region': self._tool_name_region,
            'describe_region': self._tool_describe_region,
            'batch_name_regions': self._tool_batch_name_regions,
            'list_pois': self._tool_list_pois,
            'create_poi': self._tool_create_poi,
            'update_poi': self._tool_update_poi,
            'detail_poi': self._tool_detail_poi,
            'generate_world_lore': self._tool_generate_world_lore,
            'add_historical_event': self._tool_add_historical_event,
            'log_reflection': self._tool_log_reflection,
            'get_diary': self._tool_get_diary
        }

    def run_stdio(self):
        """
        Main loop for stdio-based MCP communication.
        """
        self.running = True
        log_info("🔌 MCP Handler ready for commands")

        try:
            while self.running:
                try:
                    # Read line from stdin
                    line = sys.stdin.readline().strip()
                    if not line:
                        continue

                    # Parse JSON command
                    try:
                        command = json.loads(line)
                        response = self.handle_command(command)

                        # Send response to stdout
                        print(json.dumps(response))
                        sys.stdout.flush()

                    except json.JSONDecodeError:
                        error_response = {
                            "type": "error",
                            "message": "Invalid JSON command",
                            "command": line
                        }
                        print(json.dumps(error_response))
                        sys.stdout.flush()

                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    error_response = {
                        "type": "error",
                        "message": f"Command processing error: {str(e)}",
                        "traceback": traceback.format_exc()
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except Exception as e:
            log_info(f"MCP Handler fatal error: {e}")
            traceback.print_exc(file=sys.stderr)

        log_info("🔌 MCP Handler stopped")

    def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an MCP command with JSON-RPC 2.0 compliance.

        Args:
            command: MCP command dictionary

        Returns:
            JSON-RPC 2.0 compliant response dictionary
        """
        try:
            # Validate command is a dictionary
            if not isinstance(command, dict):
                return {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32600,
                        "message": "Invalid command format: command must be a JSON object",
                        "data": {
                            "received": str(command)
                        }
                    }
                }

            # Extract command ID for JSON-RPC compliance
            command_id = command.get('id')

            # Validate JSON-RPC protocol version
            if 'jsonrpc' not in command:
                return {
                    "jsonrpc": "2.0",
                    "id": command_id,
                    "error": {
                        "code": -32600,
                        "message": "Invalid command format: missing required 'jsonrpc' field",
                        "data": {
                            "received": command
                        }
                    }
                }

            if command.get('jsonrpc') != '2.0':
                return {
                    "jsonrpc": "2.0",
                    "id": command_id,
                    "error": {
                        "code": -32600,
                        "message": f"Invalid JSON-RPC protocol version: {command.get('jsonrpc')} (expected '2.0')",
                        "data": {
                            "received": command
                        }
                    }
                }

            # Validate command structure
            if 'tool' not in command:
                return {
                    "jsonrpc": "2.0",
                    "id": command_id,
                    "error": {
                        "code": -32600,
                        "message": "Invalid command format: missing required 'tool' field",
                        "data": {
                            "received": command
                        }
                    }
                }

            tool_name = command['tool']
            tool_args = command.get('arguments', {})

            # Find and execute tool
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](tool_args)
                    return {
                        "jsonrpc": "2.0",
                        "id": command_id,
                        "result": {
                            "type": "success",
                            "tool": tool_name,
                            "data": result,
                            "message": f"Tool {tool_name} executed successfully"
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": command_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution failed: {str(e)}",
                            "data": {
                                "tool": tool_name,
                                "error": str(e),
                                "traceback": traceback.format_exc()
                            }
                        }
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": command_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}",
                        "data": {
                            "available_tools": list(self.tools.keys())
                        }
                    }
                }

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": command_id,
                "error": {
                    "code": -32603,
                    "message": f"Command handling failed: {str(e)}",
                    "data": {
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                }
            }
            return self.validate_jsonrpc_response(error_response)

    # Tool implementations

    def _tool_create_world(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new procedural world."""
        width = args.get('width', 64)
        height = args.get('height', 64)
        seed = args.get('seed', None)
        island_mode = args.get('island_mode', True)

        world_data = self.engine.create_world(width, height, seed, island_mode)

        # Broadcast event
        self.broadcaster.emit("world_created", world_data)

        return {
            "world_id": world_data["id"],
            "width": width,
            "height": height,
            "seed": world_data["seed"],
            "island_mode": island_mode,
            "message": "World created successfully"
        }

    def _tool_get_world(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current world state."""
        world_id = args.get('world_id')
        world_data = self.engine.get_world(world_id)

        if not world_data:
            return {"error": "World not found"}

        return {
            "world": world_data,
            "message": "World retrieved successfully"
        }

    def _tool_get_statistics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get world statistics."""
        world_id = args.get('world_id')
        stats = self.engine.get_statistics(world_id)

        if not stats:
            return {"error": "World not found"}

        # Broadcast statistics update
        self.broadcaster.emit("statistics_updated", {
            "statistics": stats
        })

        return {
            "statistics": stats,
            "message": "Statistics retrieved successfully"
        }

    def _tool_get_region(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get region details."""
        world_id = args.get('world_id')
        x = args.get('x')
        y = args.get('y')

        if world_id is None or x is None or y is None:
            return {"error": "Missing required parameters"}

        region = self.engine.get_region(world_id, x, y)

        if not region:
            return {"error": "Region not found"}

        return {
            "region": region,
            "message": "Region retrieved successfully"
        }

    def _tool_name_region(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Name a region."""
        world_id = args.get('world_id')
        x = args.get('x')
        y = args.get('y')
        name = args.get('name')
        style = args.get('style', 'fantasy')

        if world_id is None or x is None or y is None or name is None:
            return {"error": "Missing required parameters"}

        region = self.engine.name_region(world_id, x, y, name, style)

        # Broadcast region naming event
        self.broadcaster.emit("region_named", {
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

    def _tool_describe_region(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rich description for a region."""
        world_id = args.get('world_id')
        x = args.get('x')
        y = args.get('y')

        if world_id is None or x is None or y is None:
            return {"error": "Missing required parameters"}

        description = self.engine.describe_region(world_id, x, y)

        # Broadcast region description event
        self.broadcaster.emit("region_described", {
            "x": x,
            "y": y,
            "description": description,
            "world_id": world_id
        })

        return {
            "description": description,
            "message": "Region described successfully"
        }

    def _tool_batch_name_regions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Name multiple regions at once."""
        world_id = args.get('world_id')
        regions = args.get('regions', [])
        style = args.get('style', 'fantasy')

        if not world_id or not regions:
            return {"error": "Missing required parameters"}

        results = []
        for region_data in regions:
            x = region_data.get('x')
            y = region_data.get('y')
            name = region_data.get('name')

            if x is None or y is None or name is None:
                continue

            region = self.engine.name_region(world_id, x, y, name, style)
            results.append(region)

            # Broadcast each region naming
            self.broadcaster.emit("region_named", {
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

    def _tool_list_pois(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all points of interest."""
        world_id = args.get('world_id')
        pois = self.engine.list_pois(world_id)

        return {
            "pois": pois,
            "count": len(pois),
            "message": "POIs listed successfully"
        }

    def _tool_create_poi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new point of interest."""
        world_id = args.get('world_id')
        poi_type = args.get('type', 'settlement')
        x = args.get('x')
        y = args.get('y')
        name = args.get('name')

        if world_id is None or x is None or y is None:
            return {"error": "Missing required parameters"}

        poi = self.engine.create_poi(world_id, poi_type, x, y, name)

        # Broadcast POI creation
        self.broadcaster.emit("poi_created", {
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

    def _tool_update_poi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing POI."""
        world_id = args.get('world_id')
        poi_id = args.get('poi_id')
        updates = args.get('updates', {})

        if world_id is None or poi_id is None:
            return {"error": "Missing required parameters"}

        poi = self.engine.update_poi(world_id, poi_id, updates)

        # Broadcast POI update
        self.broadcaster.emit("poi_updated", {
            "id": poi_id,
            "updates": updates,
            "world_id": world_id
        })

        return {
            "poi": poi,
            "message": "POI updated successfully"
        }

    def _tool_detail_poi(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed content for a POI."""
        world_id = args.get('world_id')
        poi_id = args.get('poi_id')
        detail_level = args.get('detail_level', 'medium')

        if world_id is None or poi_id is None:
            return {"error": "Missing required parameters"}

        poi = self.engine.detail_poi(world_id, poi_id, detail_level)

        # Broadcast POI detailing
        self.broadcaster.emit("poi_detailed", {
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

    def _tool_generate_world_lore(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate world lore and mythology."""
        world_id = args.get('world_id')
        lore_type = args.get('type', 'creation_myth')
        themes = args.get('themes', [])

        if world_id is None:
            return {"error": "Missing world_id"}

        lore = self.engine.generate_world_lore(world_id, lore_type, themes)

        # Broadcast lore creation
        self.broadcaster.emit("lore_created", {
            "type": lore_type,
            "content": lore["content"],
            "title": lore["title"],
            "world_id": world_id
        })

        return {
            "lore": lore,
            "message": "World lore generated successfully"
        }

    def _tool_add_historical_event(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add a historical event to world timeline."""
        world_id = args.get('world_id')
        event_type = args.get('type', 'discovery')
        description = args.get('description')
        date = args.get('date')

        if world_id is None or description is None:
            return {"error": "Missing required parameters"}

        event = self.engine.add_historical_event(world_id, event_type, description, date)

        # Broadcast historical event
        self.broadcaster.emit("historical_event_added", {
            "type": event_type,
            "description": description,
            "date": event["date"],
            "world_id": world_id
        })

        return {
            "event": event,
            "message": "Historical event added successfully"
        }

    def _tool_log_reflection(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Log a reflection to the build diary."""
        message = args.get('message')
        context = args.get('context', {})

        if not message:
            return {"error": "Missing message"}

        reflection = {
            "message": message,
            "context": context,
            "timestamp": self.engine.get_current_timestamp()
        }

        # Add to build diary
        self.broadcaster.emit("reflection_logged", {
            "message": message,
            "context": context
        })

        return {
            "reflection": reflection,
            "message": "Reflection logged successfully"
        }

    def _tool_get_diary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current build diary content."""
        diary = self.engine.get_build_diary()

        return {
            "diary": diary,
            "message": "Build diary retrieved successfully"
        }

    def validate_jsonrpc_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that a response meets JSON-RPC 2.0 specification.

        Args:
            response: Response dictionary to validate

        Returns:
            Validated response dictionary
        """
        # Ensure required fields are present
        if "jsonrpc" not in response:
            response["jsonrpc"] = "2.0"

        if "id" not in response:
            response["id"] = None  # Will be replaced by actual command ID in handle_command

        # Ensure proper structure - either result or error, not both
        has_result = "result" in response
        has_error = "error" in response

        if has_result and has_error:
            # Remove error field if result is present
            del response["error"]
        elif not has_result and not has_error:
            # Add result field if neither is present
            response["result"] = {"status": "success"}

        return response