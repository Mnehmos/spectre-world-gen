"""
SPECTRE Server Main Entry Point

Handles FastAPI web server, MCP stdio protocol, and WebSocket broadcasting.
"""

import asyncio
import threading
import queue
import sys
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn
from .mcp_handler import MCPHandler
from .world_engine import WorldEngine
from .events import EventBroadcaster

app = FastAPI(title="SPECTRE World Generator API")

# Initialize core components
engine = WorldEngine()
broadcaster = EventBroadcaster()
mcp = MCPHandler(engine, broadcaster)

# Thread-safe event queue for MCP → WebSocket communication
event_queue = queue.Queue()

def mcp_stdio_thread():
    """Run MCP handler in separate thread to avoid blocking async event loop"""
    print("🚀 MCP Handler started on stdio")
    mcp.run_stdio()

async def broadcast_loop():
    """Consume events from MCP and broadcast via WebSocket"""
    while True:
        try:
            event = await asyncio.get_event_loop().run_in_executor(
                None, event_queue.get
            )
            await broadcaster.emit(event)
        except Exception as e:
            print(f"🚨 Broadcast loop error: {e}")

# Start broadcast loop in background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_loop())

# WebSocket endpoint for live updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket client connected")

    try:
        while True:
            # Keep connection alive, actual events come from broadcaster
            await websocket.receive_text()
    except Exception as e:
        print(f"🔌 WebSocket disconnected: {e}")

# API Endpoints
@app.get("/api/world")
async def get_world():
    """Get current world state"""
    return {"world": engine.get_world_state()}

@app.get("/api/regions")
async def get_regions():
    """Get all regions"""
    return {"regions": engine.get_regions()}

@app.get("/api/pois")
async def get_pois():
    """Get all points of interest"""
    return {"pois": engine.get_pois()}

# Serve static files (web UI)
app.mount("/", StaticFiles(directory="../web", html=True), name="web")

def main():
    """Start the SPECTRE server"""
    # Start MCP handler in background thread
    mcp_thread = threading.Thread(target=mcp_stdio_thread, daemon=True)
    mcp_thread.start()

    # Start FastAPI server
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()