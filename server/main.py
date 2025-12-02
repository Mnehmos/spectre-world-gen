"""
SPECTRE World Generation Server - Main Entry Point

FastAPI server with MCP protocol support and WebSocket broadcasting.
"""

import asyncio
import threading
import queue
import sys
import json
import socket
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Default port configuration
DEFAULT_PORT = 8001
MAX_PORT_ATTEMPTS = 50


def log_info(message: str) -> None:
    """Log message to stderr to avoid corrupting MCP stdout protocol."""
    print(message, file=sys.stderr, flush=True)


def find_available_port(start_port: int = DEFAULT_PORT, max_attempts: int = MAX_PORT_ATTEMPTS) -> int:
    """
    Find an available port starting from start_port.

    Args:
        start_port: The first port to try
        max_attempts: Maximum number of ports to try

    Returns:
        An available port number

    Raises:
        RuntimeError: If no available port is found within max_attempts
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from world_engine import WorldEngine
from events import EventBroadcaster
from mcp_handler import MCPHandler
from database import DatabaseManager
from api import add_router

# Global state
app = FastAPI(title="SPECTRE World Generation Server",
              description="MCP-compatible world generation server with live visualization",
              version="0.1.0")

# Event queue for cross-thread communication
event_queue = queue.Queue()

# Initialize components
engine = WorldEngine()
broadcaster = EventBroadcaster(event_queue)
database = DatabaseManager("spectre_world.db")
mcp_handler = MCPHandler(engine, broadcaster, database)

# Add API router
add_router(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/web", StaticFiles(directory="web"), name="web")

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live event broadcasting.
    """
    await websocket.accept()
    connection_id = str(id(websocket))
    active_connections[connection_id] = websocket

    try:
        while True:
            # Wait for events from the queue
            event_data = await asyncio.get_event_loop().run_in_executor(
                None, event_queue.get
            )

            if event_data:
                try:
                    # Send event to client
                    await websocket.send_text(json.dumps(event_data))
                except Exception as e:
                    log_info(f"Error sending WebSocket message: {e}")
                    break

    except WebSocketDisconnect:
        log_info(f"Client {connection_id} disconnected")
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]

# Event broadcasting loop
async def broadcast_loop():
    """
    Process events from the queue and broadcast to all WebSocket clients.
    """
    while True:
        try:
            event_data = await asyncio.get_event_loop().run_in_executor(
                None, event_queue.get
            )

            if event_data and active_connections:
                disconnected = []
                for conn_id, websocket in active_connections.items():
                    try:
                        await websocket.send_text(json.dumps(event_data))
                    except Exception as e:
                        log_info(f"Error broadcasting to {conn_id}: {e}")
                        disconnected.append(conn_id)

                # Clean up disconnected clients
                for conn_id in disconnected:
                    if conn_id in active_connections:
                        del active_connections[conn_id]

        except Exception as e:
            log_info(f"Broadcast loop error: {e}")
            await asyncio.sleep(1)

# MCP stdio handler in separate thread
def run_mcp_stdio():
    """
    Run MCP protocol handler on stdio in separate thread.
    """
    log_info("🔌 MCP Handler started on stdio")
    try:
        mcp_handler.run_stdio()
    except Exception as e:
        log_info(f"MCP Handler error: {e}")
        event_queue.put({
            "type": "error",
            "message": f"MCP Handler failed: {str(e)}",
            "source": "server"
        })

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize server components on startup.
    """
    log_info("🚀 Starting SPECTRE World Generation Server")

    # Initialize database
    await database.initialize()

    # Start broadcast loop
    asyncio.create_task(broadcast_loop())

    # Start MCP handler in separate thread
    mcp_thread = threading.Thread(target=run_mcp_stdio, daemon=True)
    mcp_thread.start()

    # Log startup event
    event_queue.put({
        "type": "system",
        "message": "SPECTRE Server initialized",
        "status": "ready"
    })

    log_info("✅ Server initialized and ready")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown.
    """
    log_info("🛑 Shutting down SPECTRE Server")

    # Close database connections
    await database.close()

    # Notify clients
    if active_connections:
        shutdown_event = {
            "type": "system",
            "message": "Server shutting down",
            "status": "offline"
        }

        for websocket in active_connections.values():
            try:
                await websocket.send_text(json.dumps(shutdown_event))
                await websocket.close()
            except:
                pass

    event_queue.put({
        "type": "system",
        "message": "Server shutdown complete",
        "status": "offline"
    })

    log_info("✅ Server shutdown complete")

if __name__ == "__main__":
    # Find an available port with dynamic fallback
    try:
        port = find_available_port(DEFAULT_PORT)
        if port != DEFAULT_PORT:
            log_info(f"⚠️  Port {DEFAULT_PORT} is in use, using port {port} instead")
        log_info(f"🌐 Server will start on http://0.0.0.0:{port}")
    except RuntimeError as e:
        log_info(f"❌ {e}")
        sys.exit(1)

    # Configure uvicorn to log to stderr (keeps stdout clean for MCP protocol)
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr
    )

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reloader to avoid Python 3.13 compatibility issues
        log_level="info",
        access_log=False  # Disable access log to reduce stdout noise
    )