"""
BT Resume CLI - Launch the web UI and backend with a single command.

Usage:
    btr             Start server and open browser
    btr serve       Start server only (headless)
    btr setup       Install Ollama and pull model
"""

import argparse
import sys
import os
import webbrowser
import threading
import time
from pathlib import Path


def ensure_directories():
    """Ensure required directories exist."""
    from backend.config import get_resumes_dir, get_outputs_dir
    get_resumes_dir()
    get_outputs_dir()


def start_server(host="127.0.0.1", port=5000):
    """Start the Flask server."""
    # Ensure paths are set up
    backend_path = Path(__file__).parent.parent / "backend"
    core_path = Path(__file__).parent.parent / "core"
    sys.path.insert(0, str(backend_path))
    sys.path.insert(0, str(core_path))

    from backend.app import app, initialize_ollama

    # Start Ollama in background so Flask serves immediately
    def init_ollama_bg():
        print("\n[INFO] Initializing Ollama LLM Service...")
        initialize_ollama()
        print("[OK] Ollama service ready")

    thread = threading.Thread(target=init_ollama_bg, daemon=True)
    thread.start()

    print(f"\n[OK] Backend starting at http://{host}:{port}")
    print(f"[OK] Open http://{host}:{port} in your browser\n")

    app.run(host=host, port=port, debug=False, use_reloader=False)


def cmd_serve(args):
    """Start server only."""
    ensure_directories()
    start_server(args.host, args.port)


def cmd_open(args):
    """Start server and open browser."""
    ensure_directories()
    url = f"http://{args.host}:{args.port}"

    def open_browser():
        time.sleep(1.5)
        print(f"[BROWSER] Opening {url}...")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    start_server(args.host, args.port)


def cmd_setup(args):
    """Handle initial setup."""
    print("=== BT Resume Setup ===")
    print("Setting up directories...")
    ensure_directories()
    print("[OK] Directories ready")

    # Import ollama service to trigger setup
    backend_path = Path(__file__).parent.parent / "backend"
    core_path = Path(__file__).parent.parent / "core"
    sys.path.insert(0, str(backend_path))
    sys.path.insert(0, str(core_path))

    from services.ollama_service import get_ollama_service
    service = get_ollama_service()
    print("Starting Ollama service...")
    if service.startup():
        print("[OK] Ollama is ready")
        print("Downloading default model...")
        service.download_model()
        print("[OK] Setup complete!")
    else:
        print("[WARN] Ollama could not be started. Please install it manually from https://ollama.ai")


def main():
    parser = argparse.ArgumentParser(
        description="BT Resume - AI-Powered Resume Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  btr                  Start server and open browser
  btr serve            Start server only
  btr serve --port 8080  Start on custom port
  btr setup            First-time setup (Ollama + model)
        """,
    )

    parser.set_defaults(host='127.0.0.1', port=5000)

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # btr serve
    serve_parser = subparsers.add_parser("serve", help="Start the backend server")
    serve_parser.set_defaults(host='127.0.0.1', port=5000)
    serve_parser.add_argument("--host", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, help="Port to listen on")

    # btr setup
    setup_parser = subparsers.add_parser("setup", help="Run first-time setup")

    # Parse args
    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "setup":
        cmd_setup(args)
    else:
        # Default: start server and open browser
        cmd_open(args)


if __name__ == "__main__":
    main()
