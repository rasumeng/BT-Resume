"""
Backend Launcher Script

This script starts the Flask backend API server.
Called by the main application to serve the HTTP API.

Usage:
    python run_backend.py              # Use Flask development server
    python run_backend.py --gunicorn   # Use Gunicorn WSGI server
"""

import sys
import os
import atexit
import subprocess
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Add core to path  
core_path = Path(__file__).parent / "core"
sys.path.insert(0, str(core_path))

if __name__ == "__main__":
    use_gunicorn = "--gunicorn" in sys.argv
    
    from backend.app import app, initialize_ollama
    from backend.config import FLASK_HOST, FLASK_PORT
    
    print("[START] Resume AI Backend Starting...")
    print("=" * 60)
    print(f"[HOST] {FLASK_HOST}")
    print(f"[PORT] {FLASK_PORT}")
    print(f"[URL]  http://{FLASK_HOST}:{FLASK_PORT}/api")
    print(f"[MODE] {'Gunicorn' if use_gunicorn else 'Flask Development'}")
    print("=" * 60)
    
    # Initialize Ollama through app module - non-fatal if Ollama is unavailable
    print("\n[INFO] Initializing Ollama LLM Service...")
    if not initialize_ollama():
        print("\n" + "=" * 60)
        print("[WARN] Ollama is not available. Starting backend anyway.")
        print("[WARN] Some features will be disabled until Ollama is running.")
        print("=" * 60 + "\n")
    
    print("\n[OK] Backend is ready for Flutter app")
    print("[OK] Check http://localhost:5000/api/health to verify\n")
    
    if use_gunicorn:
        # Use Gunicorn WSGI server
        print("[START] Starting with Gunicorn...")
        try:
            os.chdir(str(Path(__file__).parent))
            subprocess.run(
                [
                    sys.executable, "-m", "gunicorn",
                    "--bind", f"{FLASK_HOST}:{FLASK_PORT}",
                    "--workers", "4",
                    "--worker-class", "sync",
                    "--timeout", "120",
                    "--access-logfile", "-",
                    "backend.wsgi:app"
                ],
                check=False
            )
        except KeyboardInterrupt:
            print("\n[OK] Shutdown signal received")
    else:
        # Use Flask development server
        try:
            app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            print("\n[OK] Shutdown signal received")
