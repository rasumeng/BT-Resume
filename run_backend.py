"""
Backend Launcher Script (Development Only)

Starts the Flask backend API server. Requires the package to be installed
in editable mode: pip install -e .

For production use: btr serve
"""

import sys
import os
import subprocess
from pathlib import Path

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

    print("\n[INFO] Initializing Ollama LLM Service...")
    if not initialize_ollama():
        print("\n" + "=" * 60)
        print("[WARN] Ollama is not available. Starting backend anyway.")
        print("[WARN] Some features will be disabled until Ollama is running.")
        print("=" * 60 + "\n")

    print("\n[OK] Backend is ready")
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
