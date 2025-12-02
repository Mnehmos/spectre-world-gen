#!/usr/bin/env python3
"""
SPECTRE Simple MCP Protocol Testing Script

Simplified testing focusing on MCP protocol communication without terrain generation dependencies.
"""

import json
import sys
import time
import subprocess
import threading
import requests
import websocket
import sqlite3
import os
from typing import Dict, Any, List

class SimpleMCPTester:
    """Simple MCP protocol tester without terrain generation dependencies."""

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
            # Start server using uvicorn directly to avoid subprocess issues
            self.server_process = subprocess.Popen(
                ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            time.sleep(5)
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

    def test_http_endpoints(self):
        """Test HTTP API endpoints."""
        try:
            # Test server health
            response = requests.get("http://localhost:8000", timeout=5)
            if response.status_code == 200:
                self.log_result("HTTP Server Health", True, "Server responding to HTTP requests")
            else:
                self.log_result("HTTP Server Health", False, f"Unexpected status code: {response.status_code}")

            # Test API docs
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                self.log_result("API Documentation", True, "API docs accessible")
            else:
                self.log_result("API Documentation", False, f"API docs not accessible: {response.status_code}")

        except Exception as e:
            self.log_result("HTTP Endpoint Testing", False, f"HTTP test failed: {str(e)}")

    def test_websocket_events(self):
        """Test WebSocket event broadcasting."""
        if not self.websocket_connection:
            return False

        try:
            # Send a test message to see if we get any response
            test_message = {"type": "test", "message": "WebSocket test"}
            self.websocket_connection.send(json.dumps(test_message))

            # Listen for events
            events = []
            start_time = time.time()
            timeout = 3.0

            while time.time() - start_time < timeout:
                try:
                    if self.websocket_connection.sock:
                        self.websocket_connection.sock.settimeout(0.1)
                    message = self.websocket_connection.recv()
                    if message:
                        event_data = json.loads(message)
                        events.append(event_data)
                        self.events_received.append(event_data)
                        print(f"📡 WebSocket Event: {event_data.get('type', 'unknown')}")
                except websocket.WebSocketTimeoutException:
                    continue
                except Exception as e:
                    if "timed out" in str(e).lower():
                        continue
                    break

            if events:
                self.log_result("WebSocket Event Reception", True, f"Received {len(events)} events")
                return True
            else:
                self.log_result("WebSocket Event Reception", False, "No events received")
                return False

        except Exception as e:
            self.log_result("WebSocket Testing", False, f"WebSocket test failed: {str(e)}")
            return False

    def test_database_operations(self):
        """Test database persistence operations."""
        try:
            # Test database connection
            conn = sqlite3.connect("spectre_world.db")
            cursor = conn.cursor()

            # Check if database has required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            required_tables = ['worlds', 'events', 'pois', 'lore', 'timeline']
            missing_tables = [table for table in required_tables if table not in tables]

            if not missing_tables:
                self.log_result("Database Schema", True, "All required tables exist")
            else:
                self.log_result("Database Schema", False, f"Missing tables: {', '.join(missing_tables)}")

            conn.close()
            return True

        except Exception as e:
            self.log_result("Database Operations", False, f"Database test failed: {str(e)}")
            return False

    def run_basic_tests(self):
        """Run basic connectivity tests."""
        print("🧪 Running Basic Connectivity Tests...")
        print("=" * 40)

        # Test server startup
        if not self.start_server():
            return False

        # Test WebSocket connection
        if not self.connect_websocket():
            self.stop_server()
            return False

        # Test HTTP endpoints
        self.test_http_endpoints()

        # Test WebSocket events
        self.test_websocket_events()

        # Test database
        self.test_database_operations()

        return True

    def generate_test_report(self):
        """Generate test report."""
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
            "summary": "SPECTRE Basic Connectivity Testing Complete"
        }

        # Write report to file
        with open("TEST_RESULTS_SIMPLE.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"📈 Test Results: {passed_tests}/{total_tests} passed ({pass_rate:.1f}%)")
        print(f"📡 Events Received: {len(self.events_received)}")

        # Print summary
        print("\n📝 Test Summary:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")

        return report

def main():
    """Main test execution."""
    tester = SimpleMCPTester()

    try:
        # Run basic tests
        success = tester.run_basic_tests()

        if success:
            # Generate report
            tester.generate_test_report()
            print("\n🎉 Basic Connectivity Testing Complete!")
            return 0
        else:
            print("\n❌ Basic Connectivity Testing Failed!")
            return 1

    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        return 1
    finally:
        # Cleanup
        tester.disconnect_websocket()
        tester.stop_server()

if __name__ == "__main__":
    sys.exit(main())