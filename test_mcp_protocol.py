#!/usr/bin/env python3
"""
SPECTRE MCP Protocol Testing Script

Comprehensive testing of MCP protocol communication, WebSocket broadcasting,
database persistence, and complete workflow integration.
"""

import json
import sys
import time
import subprocess
import threading
import requests
from typing import Dict, Any, List
import websocket
import sqlite3
import os

class MCPProtocolTester:
    """Test MCP protocol communication and system integration."""

    def __init__(self):
        self.server_process = None
        self.websocket_connection = None
        self.test_results = []
        self.world_id = None
        self.events_received = []

    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

    def start_server(self):
        """Start the SPECTRE server."""
        print("🚀 Starting SPECTRE server...")
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "server/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            time.sleep(3)
            return True
        except Exception as e:
            self.log_result("Server Startup", False, f"Failed to start server: {str(e)}")
            return False

    def stop_server(self):
        """Stop the SPECTRE server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            print("✅ Server stopped")

    def connect_websocket(self):
        """Connect to WebSocket server."""
        try:
            ws_url = "ws://localhost:8000/ws"
            self.websocket_connection = websocket.create_connection(ws_url)
            self.log_result("WebSocket Connection", True, f"Connected to {ws_url}")
            return True
        except Exception as e:
            self.log_result("WebSocket Connection", False, f"Failed to connect: {str(e)}")
            return False

    def disconnect_websocket(self):
        """Disconnect from WebSocket."""
        if self.websocket_connection:
            self.websocket_connection.close()
            self.websocket_connection = None

    def send_mcp_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send MCP command via stdin."""
        if not self.server_process or not self.server_process.stdin:
            return {"error": "Server process not available"}

        try:
            # Send command via stdin
            command_json = json.dumps(command)
            self.server_process.stdin.write(command_json + "\n")
            self.server_process.stdin.flush()

            # Read response from stdout
            response_line = self.server_process.stdout.readline().strip()
            return json.loads(response_line)

        except Exception as e:
            return {"error": f"MCP command failed: {str(e)}"}

    def listen_websocket_events(self, timeout: float = 5.0):
        """Listen for WebSocket events."""
        if not self.websocket_connection:
            return []

        events = []
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                if self.websocket_connection.sock and self.websocket_connection.sock.gettimeout() is None:
                    # Set a short timeout for the socket
                    self.websocket_connection.sock.settimeout(0.1)

                try:
                    message = self.websocket_connection.recv()
                    if message:
                        event_data = json.loads(message)
                        events.append(event_data)
                        self.events_received.append(event_data)
                        print(f"📡 WebSocket Event: {event_data.get('type', 'unknown')}")
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception as e:
                    if "timed out" not in str(e).lower():
                        print(f"WebSocket error: {e}")
                    break

        except Exception as e:
            print(f"Event listening error: {e}")

        return events

    def test_mcp_protocol_communication(self):
        """Test MCP protocol communication."""
        print("\n🧪 Testing MCP Protocol Communication...")

        # Test 1: Server startup
        if not self.start_server():
            return False

        # Test 2: WebSocket connection
        if not self.connect_websocket():
            self.stop_server()
            return False

        # Test 3: Create world via MCP
        create_world_cmd = {
            "tool": "create_world",
            "arguments": {
                "width": 64,
                "height": 64,
                "seed": "test_seed_123",
                "island_mode": True
            }
        }

        response = self.send_mcp_command(create_world_cmd)
        if "error" in response:
            self.log_result("MCP Create World", False, f"Error: {response['error']}")
            self.stop_server()
            return False

        if response.get("type") == "success":
            self.world_id = response["result"]["world_id"]
            self.log_result("MCP Create World", True, f"World {self.world_id} created")
        else:
            self.log_result("MCP Create World", False, "Unexpected response format")
            self.stop_server()
            return False

        # Test 4: Listen for WebSocket events
        print("📡 Waiting for WebSocket events...")
        events = self.listen_websocket_events(3.0)

        # Test 5: Verify world_created event was broadcast
        world_created_event = next((e for e in events if e.get("type") == "world_created"), None)
        if world_created_event:
            self.log_result("WebSocket Event Broadcast", True, "world_created event received")
        else:
            self.log_result("WebSocket Event Broadcast", False, "world_created event not received")
            self.stop_server()
            return False

        # Test 6: Test region operations
        region_cmd = {
            "tool": "get_region",
            "arguments": {
                "world_id": self.world_id,
                "x": 32,
                "y": 32
            }
        }

        region_response = self.send_mcp_command(region_cmd)
        if region_response.get("type") == "success":
            self.log_result("MCP Get Region", True, "Region retrieved successfully")
        else:
            self.log_result("MCP Get Region", False, f"Failed: {region_response.get('error', 'Unknown error')}")
            self.stop_server()
            return False

        # Test 7: Name a region
        name_region_cmd = {
            "tool": "name_region",
            "arguments": {
                "world_id": self.world_id,
                "x": 32,
                "y": 32,
                "name": "Eldermere",
                "style": "fantasy"
            }
        }

        name_response = self.send_mcp_command(name_region_cmd)
        if name_response.get("type") == "success":
            self.log_result("MCP Name Region", True, "Region named successfully")

            # Listen for region_named event
            print("📡 Waiting for region_named event...")
            events = self.listen_websocket_events(2.0)
            region_named_event = next((e for e in events if e.get("type") == "region_named"), None)
            if region_named_event:
                self.log_result("Region Naming Event", True, f"Region named: {region_named_event.get('data', {}).get('name', 'unknown')}")
            else:
                self.log_result("Region Naming Event", False, "region_named event not received")
        else:
            self.log_result("MCP Name Region", False, f"Failed: {name_response.get('error', 'Unknown error')}")

        # Test 8: Create POI
        poi_cmd = {
            "tool": "create_poi",
            "arguments": {
                "world_id": self.world_id,
                "type": "settlement",
                "x": 16,
                "y": 16,
                "name": "Brightwood Keep"
            }
        }

        poi_response = self.send_mcp_command(poi_cmd)
        if poi_response.get("type") == "success":
            self.log_result("MCP Create POI", True, "POI created successfully")

            # Listen for poi_created event
            print("📡 Waiting for poi_created event...")
            events = self.listen_websocket_events(2.0)
            poi_created_event = next((e for e in events if e.get("type") == "poi_created"), None)
            if poi_created_event:
                self.log_result("POI Creation Event", True, f"POI created: {poi_created_event.get('data', {}).get('name', 'unknown')}")
            else:
                self.log_result("POI Creation Event", False, "poi_created event not received")
        else:
            self.log_result("MCP Create POI", False, f"Failed: {poi_response.get('error', 'Unknown error')}")

        return True

    def test_database_persistence(self):
        """Test database persistence and recovery."""
        print("\n💾 Testing Database Persistence...")

        # Test database connection
        try:
            conn = sqlite3.connect("spectre_world.db")
            cursor = conn.cursor()

            # Check if world is saved in database
            cursor.execute("SELECT id FROM worlds WHERE id = ?", (self.world_id,))
            world_exists = cursor.fetchone() is not None

            if world_exists:
                self.log_result("Database World Save", True, "World found in database")
            else:
                self.log_result("Database World Save", False, "World not found in database")

            # Test database operations
            cursor.execute("SELECT COUNT(*) FROM pois WHERE world_id = ?", (self.world_id,))
            poi_count = cursor.fetchone()[0]

            if poi_count > 0:
                self.log_result("Database POI Save", True, f"{poi_count} POIs found in database")
            else:
                self.log_result("Database POI Save", False, "No POIs found in database")

            conn.close()

        except Exception as e:
            self.log_result("Database Operations", False, f"Database error: {str(e)}")
            return False

        # Test server restart and world recovery
        print("🔄 Testing server restart and world recovery...")
        self.stop_server()

        # Restart server
        if not self.start_server():
            return False

        # Reconnect WebSocket
        if not self.connect_websocket():
            self.stop_server()
            return False

        # Test world retrieval after restart
        get_world_cmd = {
            "tool": "get_world",
            "arguments": {
                "world_id": self.world_id
            }
        }

        world_response = self.send_mcp_command(get_world_cmd)
        if world_response.get("type") == "success":
            self.log_result("World Recovery After Restart", True, "World successfully recovered after server restart")
        else:
            self.log_result("World Recovery After Restart", False, f"Failed to recover world: {world_response.get('error', 'Unknown error')}")

        return True

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        print("\n🔄 Testing End-to-End Workflow...")

        # Test 1: Generate world lore
        lore_cmd = {
            "tool": "generate_world_lore",
            "arguments": {
                "world_id": self.world_id,
                "type": "creation_myth",
                "themes": ["ancient", "magic", "war"]
            }
        }

        lore_response = self.send_mcp_command(lore_cmd)
        if lore_response.get("type") == "success":
            self.log_result("World Lore Generation", True, "Lore generated successfully")

            # Listen for lore_created event
            events = self.listen_websocket_events(2.0)
            lore_event = next((e for e in events if e.get("type") == "lore_created"), None)
            if lore_event:
                self.log_result("Lore Creation Event", True, f"Lore event received: {lore_event.get('data', {}).get('title', 'unknown')}")
            else:
                self.log_result("Lore Creation Event", False, "lore_created event not received")
        else:
            self.log_result("World Lore Generation", False, f"Failed: {lore_response.get('error', 'Unknown error')}")

        # Test 2: Add historical event
        event_cmd = {
            "tool": "add_historical_event",
            "arguments": {
                "world_id": self.world_id,
                "type": "war",
                "description": "The Great Battle of Eldermere that changed the course of history",
                "date": "Year 123 of the Third Age"
            }
        }

        event_response = self.send_mcp_command(event_cmd)
        if event_response.get("type") == "success":
            self.log_result("Historical Event Addition", True, "Historical event added successfully")
        else:
            self.log_result("Historical Event Addition", False, f"Failed: {event_response.get('error', 'Unknown error')}")

        # Test 3: Get statistics
        stats_cmd = {
            "tool": "get_statistics",
            "arguments": {
                "world_id": self.world_id
            }
        }

        stats_response = self.send_mcp_command(stats_cmd)
        if stats_response.get("type") == "success":
            stats = stats_response.get("result", {}).get("statistics", {})
            self.log_result("World Statistics", True, f"Statistics retrieved: {stats}")
        else:
            self.log_result("World Statistics", False, f"Failed: {stats_response.get('error', 'Unknown error')}")

        # Test 4: Batch operations
        batch_name_cmd = {
            "tool": "batch_name_regions",
            "arguments": {
                "world_id": self.world_id,
                "regions": [
                    {"x": 10, "y": 10, "name": "Whispering Vale"},
                    {"x": 40, "y": 40, "name": "Blackstone Peak"},
                    {"x": 20, "y": 30, "name": "Silver Lake"}
                ],
                "style": "fantasy"
            }
        }

        batch_response = self.send_mcp_command(batch_name_cmd)
        if batch_response.get("type") == "success":
            named_count = batch_response.get("result", {}).get("named_regions", 0)
            self.log_result("Batch Region Naming", True, f"Named {named_count} regions successfully")
        else:
            self.log_result("Batch Region Naming", False, f"Failed: {batch_response.get('error', 'Unknown error')}")

        return True

    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n🛡️ Testing Error Handling...")

        # Test invalid command
        invalid_cmd = {
            "tool": "invalid_command",
            "arguments": {}
        }

        invalid_response = self.send_mcp_command(invalid_cmd)
        if invalid_response.get("type") == "error":
            self.log_result("Invalid Command Handling", True, "Invalid command properly rejected")
        else:
            self.log_result("Invalid Command Handling", False, "Invalid command not properly handled")

        # Test missing parameters
        missing_params_cmd = {
            "tool": "get_region",
            "arguments": {
                "world_id": self.world_id
                # Missing x and y
            }
        }

        missing_response = self.send_mcp_command(missing_params_cmd)
        if missing_response.get("type") == "error":
            self.log_result("Missing Parameters Handling", True, "Missing parameters properly handled")
        else:
            self.log_result("Missing Parameters Handling", False, "Missing parameters not properly handled")

        # Test invalid JSON
        try:
            self.server_process.stdin.write("invalid json data\n")
            self.server_process.stdin.flush()

            # Should get error response
            response_line = self.server_process.stdout.readline().strip()
            response = json.loads(response_line)

            if response.get("type") == "error":
                self.log_result("Invalid JSON Handling", True, "Invalid JSON properly rejected")
            else:
                self.log_result("Invalid JSON Handling", False, "Invalid JSON not properly handled")
        except Exception as e:
            self.log_result("Invalid JSON Handling", False, f"Exception during invalid JSON test: {str(e)}")

        return True

    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Generating Test Report...")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "test_session": {
                "start_time": self.test_results[0]["timestamp"] if self.test_results else time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": f"{pass_rate:.1f}%"
            },
            "test_results": self.test_results,
            "events_received": len(self.events_received),
            "event_types": list({event.get("type") for event in self.events_received}),
            "summary": "SPECTRE System Integration Testing Complete"
        }

        # Write report to file
        with open("TEST_RESULTS.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"📈 Test Results: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)")
        print(f"📡 Events Received: {len(self.events_received)}")
        print(f"📋 Event Types: {', '.join(report['event_types'])}")

        # Print summary
        print("\n📝 Test Summary:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")

        return report

    def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Starting SPECTRE Integration Testing...")
        print("=" * 50)

        try:
            # Run MCP protocol tests
            if not self.test_mcp_protocol_communication():
                print("❌ MCP Protocol tests failed - aborting")
                return False

            # Run database tests
            if not self.test_database_persistence():
                print("❌ Database tests failed - aborting")
                return False

            # Run end-to-end tests
            if not self.test_end_to_end_workflow():
                print("❌ End-to-end tests failed - aborting")
                return False

            # Run error handling tests
            if not self.test_error_handling():
                print("❌ Error handling tests failed - aborting")
                return False

            # Generate final report
            self.generate_test_report()

            print("\n✅ All tests completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Test execution failed: {str(e)}")
            return False
        finally:
            # Cleanup
            self.disconnect_websocket()
            self.stop_server()

def main():
    """Main test execution."""
    tester = MCPProtocolTester()

    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000", timeout=1)
        print("⚠️  Server is already running - tests may conflict")
    except requests.RequestException:
        pass

    # Run tests
    success = tester.run_all_tests()

    if success:
        print("\n🎉 SPECTRE Integration Testing Complete!")
        print("📊 Full test results saved to TEST_RESULTS.json")
        return 0
    else:
        print("\n❌ SPECTRE Integration Testing Failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())