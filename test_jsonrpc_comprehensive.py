#!/usr/bin/env python3
"""
Comprehensive JSON-RPC 2.0 compliance test
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

def test_jsonrpc_compliance_comprehensive():
    """Test comprehensive JSON-RPC 2.0 compliance scenarios"""

    # Create handler
    event_queue = queue.Queue()
    handler = MCPHandler(WorldEngine(), EventBroadcaster(event_queue), DatabaseManager())

    print("🧪 Running Comprehensive JSON-RPC 2.0 Compliance Tests...")
    print("=" * 60)

    test_cases = [
        {
            "name": "Valid tool execution",
            "command": {
                "jsonrpc": "2.0",
                "id": 1,
                "tool": "get_diary",
                "arguments": {}
            },
            "expected_fields": ["jsonrpc", "id", "result"],
            "should_have_result": True,
            "should_have_error": False
        },
        {
            "name": "Unknown tool",
            "command": {
                "jsonrpc": "2.0",
                "id": 2,
                "tool": "unknown_tool",
                "arguments": {}
            },
            "expected_fields": ["jsonrpc", "id", "error"],
            "should_have_result": False,
            "should_have_error": True
        },
        {
            "name": "Invalid command format",
            "command": {
                "jsonrpc": "2.0",
                "id": 3,
                "invalid_field": "test"
            },
            "expected_fields": ["jsonrpc", "id", "error"],
            "should_have_result": False,
            "should_have_error": True
        },
        {
            "name": "Command without jsonrpc field",
            "command": {
                "id": 4,
                "tool": "get_diary",
                "arguments": {}
            },
            "expected_fields": ["jsonrpc", "id", "result"],
            "should_have_result": True,
            "should_have_error": False
        },
        {
            "name": "Command without id field",
            "command": {
                "jsonrpc": "2.0",
                "tool": "get_diary",
                "arguments": {}
            },
            "expected_fields": ["jsonrpc", "id", "result"],
            "should_have_result": True,
            "should_have_error": False
        }
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Input: {json.dumps(test_case['command'], indent=2)}")

        try:
            # Test the command
            response = handler.handle_command(test_case['command'])

            print(f"Response: {json.dumps(response, indent=2)}")

            # Validate response structure
            validation_errors = []

            # Check required fields
            for field in test_case['expected_fields']:
                if field not in response:
                    validation_errors.append(f"Missing required field: {field}")

            # Check result/error structure
            has_result = 'result' in response
            has_error = 'error' in response

            if test_case['should_have_result'] and not has_result:
                validation_errors.append("Expected 'result' field but not present")
            if test_case['should_have_error'] and not has_error:
                validation_errors.append("Expected 'error' field but not present")
            if has_result and has_error:
                validation_errors.append("Response contains both 'result' and 'error' fields")
            if not test_case['should_have_result'] and not test_case['should_have_error'] and not has_result and not has_error:
                validation_errors.append("Response has neither 'result' nor 'error' field")

            # Validate JSON-RPC fields
            if 'jsonrpc' in response and response['jsonrpc'] != '2.0':
                validation_errors.append(f"Invalid jsonrpc value: {response['jsonrpc']}")

            if validation_errors:
                print(f"❌ Validation Errors:")
                for error in validation_errors:
                    print(f"  - {error}")
                all_passed = False
            else:
                print(f"✅ JSON-RPC 2.0 Compliance Validated")

        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All JSON-RPC 2.0 compliance tests passed!")
        return True
    else:
        print("❌ Some JSON-RPC 2.0 compliance tests failed!")
        return False

def test_protocol_validation_layer():
    """Test the protocol validation layer functionality"""

    print("\n🔍 Testing Protocol Validation Layer...")

    event_queue = queue.Queue()
    handler = MCPHandler(WorldEngine(), EventBroadcaster(event_queue), DatabaseManager())

    # Test validation layer with various response structures
    test_responses = [
        {
            "name": "Complete valid response",
            "input": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "success"}
            },
            "expected": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "success"}
            }
        },
        {
            "name": "Missing jsonrpc field",
            "input": {
                "id": 1,
                "result": {"status": "success"}
            },
            "expected": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "success"}
            }
        },
        {
            "name": "Missing id field",
            "input": {
                "jsonrpc": "2.0",
                "result": {"status": "success"}
            },
            "expected": {
                "jsonrpc": "2.0",
                "id": None,
                "result": {"status": "success"}
            }
        },
        {
            "name": "Both result and error present",
            "input": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "success"},
                "error": {"code": -32600, "message": "error"}
            },
            "expected": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "success"}
            }
        },
        {
            "name": "Neither result nor error present",
            "input": {
                "jsonrpc": "2.0",
                "id": 1
            },
            "expected": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"status": "success"}
            }
        }
    ]

    all_passed = True

    for test in test_responses:
        print(f"\n📋 Testing: {test['name']}")
        print(f"Input: {json.dumps(test['input'], indent=2)}")

        validated_response = handler.validate_jsonrpc_response(test['input'])

        print(f"Validated: {json.dumps(validated_response, indent=2)}")
        print(f"Expected: {json.dumps(test['expected'], indent=2)}")

        # Compare results
        if validated_response == test['expected']:
            print(f"✅ Validation layer working correctly")
        else:
            print(f"❌ Validation layer output differs from expected")
            all_passed = False

    return all_passed

if __name__ == "__main__":
    success1 = test_jsonrpc_compliance_comprehensive()
    success2 = test_protocol_validation_layer()

    if success1 and success2:
        print("\n🎉 All JSON-RPC 2.0 compliance tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some JSON-RPC 2.0 compliance tests failed!")
        sys.exit(1)