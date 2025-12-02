#!/usr/bin/env python3
"""
Direct WebSocket Testing Script

Test WebSocket connection and event broadcasting directly.
"""

import json
import sys
import time
import websocket
import requests

def test_websocket_connection():
    """Test WebSocket connection."""
    print("🧪 Testing WebSocket Connection...")

    try:
        # Test WebSocket connection
        ws_url = "ws://localhost:8000/ws"
        print(f"🔌 Connecting to {ws_url}...")

        ws = websocket.create_connection(ws_url)
        print("✅ WebSocket connection established!")

        # Send a test message
        test_message = {"type": "test", "message": "Hello SPECTRE!"}
        ws.send(json.dumps(test_message))
        print(f"📤 Sent test message: {test_message}")

        # Listen for events
        print("📡 Waiting for WebSocket events...")
        events_received = []

        start_time = time.time()
        while time.time() - start_time < 5.0:
            try:
                message = ws.recv()
                if message:
                    event_data = json.loads(message)
                    events_received.append(event_data)
                    print(f"📋 Received event: {event_data.get('type', 'unknown')}")
                    print(f"    Data: {json.dumps(event_data.get('data', {}), indent=2)}")
            except websocket.WebSocketTimeoutException:
                continue
            except Exception as e:
                print(f"⚠️ WebSocket error: {e}")
                break

        ws.close()
        print(f"✅ Test complete. Received {len(events_received)} events.")

        return True, events_received

    except Exception as e:
        print(f"❌ WebSocket test failed: {str(e)}")
        return False, []

def test_http_api():
    """Test HTTP API endpoints."""
    print("\n🔗 Testing HTTP API Endpoints...")

    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            health_data = response.json()
            print(f"    Health data: {json.dumps(health_data, indent=2)}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")

        # Test API docs
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")

    except Exception as e:
        print(f"❌ API test failed: {str(e)}")

def main():
    """Main test execution."""
    print("🚀 SPECTRE WebSocket & API Testing")
    print("=" * 40)

    # Test WebSocket
    ws_success, events = test_websocket_connection()

    # Test HTTP API
    test_http_api()

    if ws_success:
        print(f"\n🎉 WebSocket testing complete!")
        print(f"📊 Received {len(events)} WebSocket events")
        return 0
    else:
        print(f"\n❌ WebSocket testing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())