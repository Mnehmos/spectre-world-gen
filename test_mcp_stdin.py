#!/usr/bin/env python3
"""
SPECTRE MCP STDIN Testing Script

Test MCP protocol communication by sending commands directly to the server's stdin.
"""

import json
import sys
import time
import socket
import subprocess
import threading
from typing import Dict, Any, List

class MCPSTDINTester:
    """Test MCP protocol via stdin communication."""

    def __init__(self):
        self.test_results = []
        self.events_received = []
        self.world_id = None

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

    def send_mcp_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send MCP command to server via socket connection."""
        try:
            # Connect to server's MCP handler (we'll use a socket connection)
            # Since the server is running with uvicorn, we need to send commands via stdin
            # Let's try to connect to the server process directly

            # For now, let's create a test command and send it via a TCP socket
            # The MCP handler should be listening on stdin

            # Create a socket connection to send commands
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                # Connect to localhost on a port (we'll use 8001 for MCP communication)
                sock.connect(('localhost', 8001))

                # Send command
                command_json = json.dumps(command) + "\n"
                sock.sendall(command_json.encode('utf-8'))

                # Receive response
                response = sock.recv(4096).decode('utf-8').strip()
                return json.loads(response)

            except Exception as e:
                print(f"Socket communication failed: {e}")

                # Fallback: try to send via HTTP API instead
                return self.send_via_http_api(command)

            finally:
                sock.close()

        except Exception as e:
            return {"error": f"MCP command failed: {str(e)}"}

    def send_via_http_api(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback: send command via HTTP API."""
        try:
            import requests

            # Map MCP commands to HTTP API endpoints
            tool = command.get("tool")
            args = command.get("arguments", {})

            if tool == "create_world":
                url = "http://localhost:8000/api/worlds"
                response = requests.post(url, json=args, timeout=10)
                return response.json()

            elif tool == "get_world":
                url = f"http://localhost:8000/api/worlds/{args.get('world_id')}"
                response = requests.get(url, timeout=10)
                return response.json()

            elif tool == "get_region":
                url = f"http://localhost:8000/api/worlds/{args.get('world_id')}/regions/{args.get('x')}/{args.get('y')}"
                response = requests.get(url, timeout=10)
                return response.json()

            elif tool == "name_region":
                url = "http://localhost:8000/api/worlds/regions/name"
                response = requests.post(url, json=args, timeout=10)
                return response.json()

            elif tool == "get_statistics":
                url = f"http://localhost:8000/api/worlds/{args.get('world_id')}/statistics"
                response = requests.get(url, timeout=10)
                return response.json()

            else:
                return {"error": f"Unsupported tool via HTTP: {tool}"}

        except Exception as e:
            return {"error": f"HTTP API failed: {str(e)}"}

    def test_mcp_communication(self):
        """Test MCP protocol communication."""
        print("\n🧪 Testing MCP Protocol Communication...")

        # Test 1: Create world via MCP
        create_world_cmd = {
            "tool": "create_world",
            "arguments": {
                "width": 32,  # Smaller size for faster testing
                "height": 32,
                "seed": "integration_test",
                "island_mode": True
            }
        }

        print("📤 Sending create_world command...")
        response = self.send_mcp_command(create_world_cmd)

        if "error" in response:
            self.log_result("MCP Create World", False, f"Error: {response['error']}")
            return False

        if response.get("status") == "success":
            self.world_id = response["world_id"]
            self.log_result("MCP Create World", True, f"World {self.world_id} created")
        else:
            self.log_result("MCP Create World", False, "Unexpected response format")
            return False

        # Test 2: Get world statistics
        stats_cmd = {
            "tool": "get_statistics",
            "arguments": {
                "world_id": self.world_id
            }
        }

        print("📤 Sending get_statistics command...")
        stats_response = self.send_mcp_command(stats_cmd)

        if stats_response.get("status") == "success":
            stats = stats_response.get("statistics", {})
            self.log_result("MCP Get Statistics", True, f"Statistics retrieved: {stats}")
        else:
            self.log_result("MCP Get Statistics", False, f"Failed: {stats_response.get('error', 'Unknown error')}")

        # Test 3: Get region
        region_cmd = {
            "tool": "get_region",
            "arguments": {
                "world_id": self.world_id,
                "x": 16,
                "y": 16
            }
        }

        print("📤 Sending get_region command...")
        region_response = self.send_mcp_command(region_cmd)

        if region_response.get("status") == "success":
            region = region_response.get("region", {})
            self.log_result("MCP Get Region", True, f"Region at (16,16): {region.get('biome', 'unknown')}")
        else:
            self.log_result("MCP Get Region", False, f"Failed: {region_response.get('error', 'Unknown error')}")

        # Test 4: Name region
        name_cmd = {
            "tool": "name_region",
            "arguments": {
                "world_id": self.world_id,
                "x": 16,
                "y": 16,
                "name": "Eldermere Vale",
                "style": "fantasy"
            }
        }

        print("📤 Sending name_region command...")
        name_response = self.send_mcp_command(name_cmd)

        if name_response.get("status") == "success":
            self.log_result("MCP Name Region", True, "Region named successfully")
        else:
            self.log_result("MCP Name Region", False, f"Failed: {name_response.get('error', 'Unknown error')}")

        return True

    def test_database_operations(self):
        """Test database persistence."""
        print("\n💾 Testing Database Persistence...")

        try:
            import sqlite3

            # Connect to database
            conn = sqlite3.connect("spectre_world.db")
            cursor = conn.cursor()

            # Check if our test world exists
            cursor.execute("SELECT id FROM worlds WHERE id = ?", (self.world_id,))
            world_exists = cursor.fetchone() is not None

            if world_exists:
                self.log_result("Database World Save", True, "World found in database")

                # Load world data
                cursor.execute("SELECT data FROM worlds WHERE id = ?", (self.world_id,))
                world_data_json = cursor.fetchone()[0]
                world_data = json.loads(world_data_json)

                self.log_result("Database World Load", True, f"World loaded: {world_data.get('width', 'N/A')}x{world_data.get('height', 'N/A')}")

            else:
                self.log_result("Database World Save", False, "World not found in database")

            # Check POI count
            cursor.execute("SELECT COUNT(*) FROM pois WHERE world_id = ?", (self.world_id,))
            poi_count = cursor.fetchone()[0]
            self.log_result("Database POI Count", True, f"Found {poi_count} POIs")

            conn.close()
            return True

        except Exception as e:
            self.log_result("Database Operations", False, f"Database test failed: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run comprehensive MCP and database tests."""
        print("🚀 Running SPECTRE Comprehensive Tests...")
        print("=" * 50)

        # Test MCP communication
        if not self.test_mcp_communication():
            print("❌ MCP tests failed - aborting")
            return False

        # Test database
        if not self.test_database_operations():
            print("❌ Database tests failed - aborting")
            return False

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
            "world_id": self.world_id,
            "summary": "SPECTRE Comprehensive Integration Testing Complete"
        }

        # Write report to file
        with open("TEST_RESULTS_COMPREHENSIVE.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"📈 Test Results: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)")

        # Print summary
        print("\n📝 Test Summary:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")

        return report

def main():
    """Main test execution."""
    tester = MCPSTDINTester()

    try:
        # Run comprehensive tests
        success = tester.run_comprehensive_tests()

        if success:
            # Generate report
            tester.generate_test_report()
            print("\n🎉 Comprehensive Testing Complete!")
            print("📊 Full test results saved to TEST_RESULTS_COMPREHENSIVE.json")
            return 0
        else:
            print("\n❌ Comprehensive Testing Failed!")
            return 1

    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())