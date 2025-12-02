"""
SPECTRE Server Runner

Handles proper module imports and runs the FastAPI server.
"""

import sys
import os

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
    print("✅ Applied Python 3.13 compatibility patch for linecache.py")
except Exception as e:
    print(f"⚠️  Could not apply linecache patch: {e}")

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
    print("🚀 Starting SPECTRE World Generation Server...")
    print("📁 Project root:", project_root)
    print("🐍 Python path updated with project directories")

    # Import and run the main module
    import importlib
    main_module = importlib.import_module('server.main')

    # Check if the module has the expected components
    if hasattr(main_module, 'app'):
        print("✅ FastAPI app found")
    else:
        print("❌ FastAPI app not found")

    # Call uvicorn.run directly since we're importing, not executing as __main__
    import uvicorn
    try:
        uvicorn.run(
            "server.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reloader to avoid Python 3.13 compatibility issues
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start uvicorn: {e}")
        print("ℹ️ This might be due to missing dependencies. Please run:")
        print("pip install fastapi uvicorn websockets")