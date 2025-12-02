#!/usr/bin/env python3
"""
Test script to reproduce JSON-RPC validation errors
"""

import json
import sys
import os
import queue

# Add current directory to path
sys.path.append('.')

from server.mcp_handler import MCPHandler
from server.world_engine import WorldEngine
from server.events import EventBroadcaster
from server.database import DatabaseManager

def test_jsonrpc_compliance():
    """Test current MCP responses for JSON-RPC compliance"""

    # Create event queue and handler
    event_queue = queue.Queue()
    handler = MCPHandler(WorldEngine(), EventBroadcaster(event_queue), DatabaseManager())

    # Test command with JSON-RPC format - use a simpler tool first
    test_command = {
        "jsonrpc": "2.0",
        "id": 1,
        "tool": "get_diary",
        "arguments": {}
    }

    print("🧪 Testing JSON-RPC compliance...")
    print(f"Input command: {json.dumps(test_command, indent=2)}")

    # Test current response format
    response = handler.handle_command(test_command)

    print(f"Current response: {json.dumps(response, indent=2)}")

    # Validate JSON-RPC compliance
    errors = []

    # Check for required fields
    if "jsonrpc" not in response:
        errors.append("Missing required 'jsonrpc' field")
    elif response["jsonrpc"] != "2.0":
        errors.append(f"Invalid 'jsonrpc' value: {response['jsonrpc']} (expected '2.0')")

    if "id" not in response:
        errors.append("Missing required 'id' field")

    # Check response structure
    if "result" not in response and "error" not in response:
        errors.append("Missing both 'result' and 'error' fields")

    if errors:
        print("❌ JSON-RPC Validation Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ JSON-RPC compliance validated")
        return True

if __name__ == "__main__":
    test_jsonrpc_compliance()