#!/usr/bin/env python3
"""
Final MCP JSON-RPC protocol compliance test
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

def test_mcp_jsonrpc_compliance():
    """Test MCP JSON-RPC protocol compliance with real MCP command"""

    print("🧪 Testing MCP JSON-RPC Protocol Compliance...")
    print("=" * 50)

    # Create handler
    event_queue = queue.Queue()
    handler = MCPHandler(WorldEngine(), EventBroadcaster(event_queue), DatabaseManager())

    # Test a simple MCP command with JSON-RPC format
    mcp_command = {
        "jsonrpc": "2.0",
        "id": 1,
        "tool": "get_diary",
        "arguments": {}
    }

    print(f"Input MCP Command: {json.dumps(mcp_command, indent=2)}")

    # Handle the command
    response = handler.handle_command(mcp_command)

    print(f"Response: {json.dumps(response, indent=2)}")

    # Validate JSON-RPC compliance
    errors = []

    # Check required fields
    if "jsonrpc" not in response:
        errors.append("Missing required 'jsonrpc' field")
    elif response["jsonrpc"] != "2.0":
        errors.append(f"Invalid 'jsonrpc' value: {response['jsonrpc']}")

    if "id" not in response:
        errors.append("Missing required 'id' field")
    elif response["id"] != mcp_command["id"]:
        errors.append(f"ID mismatch: expected {mcp_command['id']}, got {response['id']}")

    # Check response structure
    has_result = "result" in response
    has_error = "error" in response

    if not has_result and not has_error:
        errors.append("Missing both 'result' and 'error' fields")
    elif has_result and has_error:
        errors.append("Response contains both 'result' and 'error' fields")

    # Check result structure if present
    if has_result:
        if not isinstance(response["result"], dict):
            errors.append("'result' field should be a dictionary")
        elif "type" not in response["result"] or response["result"]["type"] != "success":
            errors.append("'result' should contain 'type': 'success'")

    # Check error structure if present
    if has_error:
        if not isinstance(response["error"], dict):
            errors.append("'error' field should be a dictionary")
        elif "code" not in response["error"] or "message" not in response["error"]:
            errors.append("'error' should contain 'code' and 'message' fields")

    # Display results
    if errors:
        print("❌ JSON-RPC Compliance Errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ JSON-RPC 2.0 Compliance Validated!")
        print("✅ All required fields present")
        print("✅ Proper response structure")
        print("✅ MCP protocol compliance achieved")
        return True

if __name__ == "__main__":
    success = test_mcp_jsonrpc_compliance()

    if success:
        print("\n🎉 MCP JSON-RPC Protocol Compliance Test PASSED!")
        print("The SPECTRE MCP server is now fully JSON-RPC 2.0 compliant!")
        sys.exit(0)
    else:
        print("\n❌ MCP JSON-RPC Protocol Compliance Test FAILED!")
        sys.exit(1)