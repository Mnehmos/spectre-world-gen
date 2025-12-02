"""
MCP Protocol Handler

Manages communication with Kilo Code via stdio protocol.
"""

import json
import sys
from .events import EventBroadcaster

class MCPHandler:
    def __init__(self, world_engine, broadcaster: EventBroadcaster):
        self.engine = world_engine
        self.broadcaster = broadcaster
        self.tools = self._register_tools()

    def _register_tools(self):
        """Register all available MCP tools"""
        return {
            "create_world": self.create_world,
            "get_world": self.get_world,
            "get_region": self.get_region,
            "name_region": self.name_region,
            "batch_name_regions": self.batch_name_regions,
            "create_poi": self.create_poi,
            "update_poi": self.update_poi,
            "detail_poi": self.detail_poi,
            "generate_world_lore": self.generate_world_lore,
            "log_reflection": self.log_reflection
        }

    def run_stdio(self):
        """Main stdio loop for MCP communication"""
        print("🔧 MCP Handler ready for input")

        while True:
            try:
                line = sys.stdin.readline().strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and "tool" in data:
                        self.handle_tool_call(data)
                except json.JSONDecodeError:
                    print(f"🚨 Invalid JSON: {line}")

            except KeyboardInterrupt:
                print("👋 MCP Handler shutting down")
                break
            except Exception as e:
                print(f"🚨 MCP Handler error: {e}")

    def handle_tool_call(self, data):
        """Handle incoming tool calls from MCP"""
        tool_name = data.get("tool")
        params = data.get("params", {})

        if tool_name in self.tools:
            try:
                result = self.tools[tool_name](**params)

                # Broadcast event for this tool call
                event_type = f"{tool_name}_called"
                event_data = {
                    "type": event_type,
                    "params": params,
                    "result": result
                }
                self.broadcaster.emit(event_data)

                # Return result via stdout
                response = {
                    "status": "success",
                    "tool": tool_name,
                    "result": result
                }
                print(json.dumps(response))
            except Exception as e:
                error_response = {
                    "status": "error",
                    "tool": tool_name,
                    "error": str(e)
                }
                print(json.dumps(error_response))
        else:
            error_response = {
                "status": "error",
                "tool": tool_name,
                "error": "Tool not found"
            }
            print(json.dumps(error_response))

    # Tool implementations
    def create_world(self, seed: int = 42, size: int = 64, island_mode: bool = True):
        """Generate a new procedural world"""
        return self.engine.create_world(seed, size, island_mode)

    def get_world(self):
        """Get current world state"""
        return self.engine.get_world_state()

    def get_region(self, x: int, y: int):
        """Get region details"""
        return self.engine.get_region(x, y)

    def name_region(self, x: int, y: int, name: str, biome: str):
        """Name a region"""
        result = self.engine.name_region(x, y, name, biome)
        self.broadcaster.emit({
            "type": "region_named",
            "x": x,
            "y": y,
            "name": name,
            "biome": biome
        })
        return result

    def batch_name_regions(self, regions: list):
        """Name multiple regions"""
        results = []
        for region in regions:
            result = self.name_region(**region)
            results.append(result)
        return results

    def create_poi(self, poi_type: str, x: int, y: int, name: str = ""):
        """Create a new point of interest"""
        result = self.engine.create_poi(poi_type, x, y, name)
        self.broadcaster.emit({
            "type": "poi_created",
            "poi_id": result["id"],
            "poi_type": poi_type,
            "x": x,
            "y": y,
            "name": name or result["name"]
        })
        return result

    def update_poi(self, poi_id: str, updates: dict):
        """Update a point of interest"""
        result = self.engine.update_poi(poi_id, updates)
        self.broadcaster.emit({
            "type": "poi_updated",
            "poi_id": poi_id,
            "updates": updates
        })
        return result

    def detail_poi(self, poi_id: str):
        """Generate detailed information for a POI"""
        result = self.engine.detail_poi(poi_id)
        self.broadcaster.emit({
            "type": "poi_detailed",
            "poi_id": poi_id,
            **result
        })
        return result

    def generate_world_lore(self, lore_type: str, theme: str = "fantasy"):
        """Generate world lore"""
        result = self.engine.generate_world_lore(lore_type, theme)
        self.broadcaster.emit({
            "type": "lore_created",
            "lore_type": lore_type,
            "theme": theme,
            "content": result["content"]
        })
        return result

    def log_reflection(self, entry_type: str, content: str):
        """Log a reflection to the build diary"""
        result = self.engine.log_reflection(entry_type, content)
        self.broadcaster.emit({
            "type": "diary_updated",
            "entry_type": entry_type,
            "content": content
        })
        return result