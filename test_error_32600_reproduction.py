#!/usr/bin/env python3
"""
Test script to reproduce and analyze MCP Error -32600 scenarios
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

def test_error_32600_scenarios():
    """Test various scenarios that might trigger Error -32600"""

    print("🔍 Testing MCP Error -32600 Scenarios...")
    print("=" * 50)

    # Create handler
    event_queue = queue.Queue()
    handler = MCPHandler(WorldEngine(), EventBroadcaster(event_queue), DatabaseManager())

    # Test cases that should trigger Error -32600
    error_32600_cases = [
        {
            "name": "Missing 'tool' field",
            "command": {
                "jsonrpc": "2.0",
                "id": 1,
                "arguments": {}
            }
        },
        {
            "name": "Invalid command structure (not a dict)",
            "command": "invalid_command_string"
        },
        {
            "name": "Empty command",
            "command": {}
        },
        {
            "name": "Command with only invalid fields",
            "command": {
                "jsonrpc": "2.0",
                "id": 2,
                "random_field": "value",
                "another_field": "data"
            }
        },
        {
            "name": "Command with wrong structure",
            "command": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "get_diary",  # Should be 'tool', not 'method'
                "params": {}  # Should be 'arguments', not 'params'
            }
        }
    ]

    all_passed = True

    for test_case in error_32600_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"Input: {json.dumps(test_case['command'], indent=2) if isinstance(test_case['command'], dict) else test_case['command']}")

        try:
            # Test the command
            response = handler.handle_command(test_case['command'])

            print(f"Response: {json.dumps(response, indent=2)}")

            # Check if we got Error -32600
            if "error" in response and response["error"]["code"] == -32600:
                print(f"✅ Correctly returned Error -32600: {response['error']['message']}")
            elif "error" in response:
                print(f"⚠️  Returned different error: {response['error']['code']} - {response['error']['message']}")
            else:
                print(f"❌ Expected Error -32600 but got success response")
                all_passed = False

        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All Error -32600 scenarios handled correctly")
        return True
    else:
        print("❌ Some Error -32600 scenarios not handled correctly")
        return False

def test_jsonrpc_protocol_strict_compliance():
    """Test strict JSON-RPC 2.0 protocol compliance"""

    print("\n🔍 Testing Strict JSON-RPC 2.0 Protocol Compliance...")
    print("=" * 60)

    event_queue = queue.Queue()
    handler = MCPHandler(WorldEngine(), EventBroadcaster(event_queue), DatabaseManager())

    # Test cases for strict protocol compliance
    strict_test_cases = [
        {
            "name": "Valid JSON-RPC 2.0 command",
            "command": {
                "jsonrpc": "2.0",
                "id": 1,
                "tool": "get_diary",
                "arguments": {}
            },
            "should_pass": True
        },
        {
            "name": "Command without jsonrpc field",
            "command": {
                "id": 2,
                "tool": "get_diary",
                "arguments": {}
            },
            "should_pass": False  # Should fail validation
        },
        {
            "name": "Command with wrong jsonrpc version",
            "command": {
                "jsonrpc": "1.0",
                "id": 3,
                "tool": "get_diary",
                "arguments": {}
            },
            "should_pass": False  # Should fail validation
        },
        {
            "name": "Command with null id",
            "command": {
                "jsonrpc": "2.0",
                "id": None,
                "tool": "get_diary",
                "arguments": {}
            },
            "should_pass": True  # Null id is allowed in JSON-RPC 2.0
        },
        {
            "name": "Command with string id",
            "command": {
                "jsonrpc": "2.0",
                "id": "req1",
                "tool": "get_diary",
                "arguments": {}
            },
            "should_pass": True  # String ids are allowed in JSON-RPC 2.0
        }
    ]

    all_passed = True

    for test_case in strict_test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print(f"Input: {json.dumps(test_case['command'], indent=2)}")

        try:
            response = handler.handle_command(test_case['command'])

            # Check if response is valid JSON-RPC 2.0
            is_valid = (
                "jsonrpc" in response and
                response["jsonrpc"] == "2.0" and
                "id" in response
            )

            if test_case['should_pass']:
                if is_valid and "result" in response:
                    print(f"✅ Valid JSON-RPC 2.0 response")
                else:
                    print(f"❌ Expected valid response but got invalid format")
                    all_passed = False
            else:
                if is_valid and "error" in response:
                    print(f"✅ Correctly rejected invalid command")
                else:
                    print(f"❌ Expected rejection but got: {json.dumps(response, indent=2)}")
                    all_passed = False

        except Exception as e:
            print(f"❌ Exception occurred: {str(e)}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All strict JSON-RPC 2.0 protocol compliance tests passed")
        return True
    else:
        print("❌ Some strict JSON-RPC 2.0 protocol compliance tests failed")
        return False

if __name__ == "__main__":
    success1 = test_error_32600_scenarios()
    success2 = test_jsonrpc_protocol_strict_compliance()

    if success1 and success2:
        print("\n🎉 All MCP Error -32600 and protocol compliance tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some MCP Error -32600 or protocol compliance tests failed!")
        sys.exit(1)