"""
SPECTRE Server Runner

Handles proper module imports and runs the FastAPI server.
"""

import sys
import os
import socket

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


# Python 3.13 compatibility fix for linecache.py
# This monkey patch handles the AttributeError: 'str' object has no attribute 'co_consts'
try:
    import linecache
    original_register_code = linecache._register_code

    def safe_register_code(code, file, module_globals):
        try:
            # Check if code is actually a code object with co_consts attribute
            if hasattr(code, 'co_consts'):
                original_register_code(code, file, module_globals)
        except (AttributeError, TypeError):
            # Skip problematic code objects (like strings)
            pass

    linecache._register_code = safe_register_code
    log_info("✅ Applied Python 3.13 compatibility patch for linecache.py")
except Exception as e:
    log_info(f"⚠️  Could not apply linecache patch: {e}")

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'server'))
sys.path.insert(0, os.path.join(project_root, 'terrain'))
sys.path.insert(0, os.path.join(project_root, 'tools'))

# Now run the main server
import server.main

if __name__ == "__main__":
    # This will execute the uvicorn.run() from main.py
    log_info("🚀 Starting SPECTRE World Generation Server...")
    log_info(f"📁 Project root: {project_root}")
    log_info("🐍 Python path updated with project directories")

    # Import and run the main module
    import importlib
    main_module = importlib.import_module('server.main')

    # Check if the module has the expected components
    if hasattr(main_module, 'app'):
        log_info("✅ FastAPI app found")
    else:
        log_info("❌ FastAPI app not found")

    # Call uvicorn.run directly since we're importing, not executing as __main__
    import uvicorn
    import logging

    # Configure uvicorn to log to stderr (keeps stdout clean for MCP protocol)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr
    )

    # Find an available port with dynamic fallback
    try:
        port = find_available_port(DEFAULT_PORT)
        if port != DEFAULT_PORT:
            log_info(f"⚠️  Port {DEFAULT_PORT} is in use, using port {port} instead")
        log_info(f"🌐 Server will start on http://0.0.0.0:{port}")
    except RuntimeError as e:
        log_info(f"❌ {e}")
        sys.exit(1)

    try:
        uvicorn.run(
            "server.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # Disable reloader to avoid Python 3.13 compatibility issues
            log_level="info",
            access_log=False  # Disable access log to reduce stdout noise
        )
    except Exception as e:
        log_info(f"❌ Failed to start uvicorn: {e}")
        log_info("ℹ️ This might be due to missing dependencies. Please run:")
        log_info("pip install fastapi uvicorn websockets")