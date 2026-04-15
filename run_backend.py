"""
Backend Launcher Script

This script starts the Flask backend API server.
Called by the main application to serve the HTTP API.

Usage:
    python run_backend.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Add core to path  
core_path = Path(__file__).parent / "core"
sys.path.insert(0, str(core_path))

if __name__ == "__main__":
    from backend.app import app
    from backend.config import FLASK_HOST, FLASK_PORT
    
    print("═" * 60)
    print("🚀 Resume AI Backend Starting...")
    print("═" * 60)
    print(f"📍 Host: {FLASK_HOST}")
    print(f"🔌 Port: {FLASK_PORT}")
    print(f"🌐 API Base: http://{FLASK_HOST}:{FLASK_PORT}/api")
    print("═" * 60)
    print("\n✓ Backend is ready for Flutter app")
    print("✓ Check http://localhost:5000/api/health to verify\n")
    
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
