"""
Flask Backend for BT-Resume - Local AI Service Layer
Manages all resume processing and API endpoints.
"""

import logging
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import atexit
from pathlib import Path

# ─── Setup Logging (BEFORE any other imports) ───
# Suppress verbose Flask/Werkzeug logs - only show critical info
logging.basicConfig(
    level=logging.WARNING,  # Only show WARNING and ERROR
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True  # Force reconfiguration even if already configured
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Our app logs at INFO level

# Suppress Flask and Werkzeug debug logging (users don't need to see these)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)  # Only show werkzeug errors
flask_logger = logging.getLogger('flask')
flask_logger.setLevel(logging.ERROR)  # Only show flask errors
flask_logger.propagate = False

from backend.config import FLASK_HOST, FLASK_PORT, OLLAMA_HOST, get_resumes_dir, get_outputs_dir
from backend.services.ollama_service import get_ollama_service

# ─── Initialize Required Directories ───
logger.info("=" * 60)
logger.info("[APP] Initializing application directories...")
logger.info("=" * 60)

try:
    resumes_dir = get_resumes_dir()
    logger.info(f"[OK] Resumes directory ready: {resumes_dir}")
    
    outputs_dir = get_outputs_dir()
    logger.info(f"[OK] Outputs directory ready: {outputs_dir}")
except Exception as e:
    logger.error(f"[ERR] Failed to initialize directories: {e}")
    sys.exit(1)

# ─── Flask App Setup ───
app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# ─── Ollama Service Initialization ───
ollama_service = get_ollama_service()
logger.info("[APP] app.py: Got Ollama service instance")


def initialize_ollama():
    """Initialize Ollama service. Called by run_backend.py."""
    logger.info("=" * 60)
    logger.info("[APP] Initializing Ollama LLM Service from app.py...")
    logger.info(f"[APP] Service instance ID: {id(ollama_service)}")
    logger.info("=" * 60)
    
    logger.info(f"[APP] Before startup: is_ready={ollama_service.is_ready}")
    success = ollama_service.startup()
    logger.info(f"[APP] After startup: is_ready={ollama_service.is_ready}, success={success}")
    
    if success:
        logger.info("[OK] Ollama service initialized successfully in app!")
        logger.info(f"Ollama is_ready flag: {ollama_service.is_ready}")
        return True
    else:
        logger.warning("[WARN] Ollama service failed to initialize. Please ensure Ollama is installed and running: https://ollama.ai")
        logger.info(f"[APP] Ollama is_ready flag: {ollama_service.is_ready}")
        return False


@app.before_request
def inject_ollama_service():
    """Inject Ollama service into request context."""
    from flask import g
    logger.debug(f"[DEBUG] before_request: injecting ollama_service instance")
    g.ollama_service = ollama_service
    logger.debug(f"[DEBUG] before_request: g.ollama_service is now set with is_ready={g.ollama_service.is_ready}")


# ─── Health Check Endpoint (Critical for Startup) ───
@app.route("/api/health", methods=["GET"])
def health():
    """
    Health check endpoint - used by Flutter to verify backend is ready.
    This should be the FIRST thing Flutter checks when launching.
    """
    return jsonify(
        {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "resume-ai-api",
            "llm_ready": ollama_service.is_ready,
        }
    )


# ─── Status Endpoint ───
@app.route("/api/status", methods=["GET"])
def status():
    """Get detailed status of all services."""
    return jsonify(
        {
            "api": "running",
            "ollama": ollama_service.get_status(),
            "ollama_is_ready": ollama_service.is_ready,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ─── Register Route Blueprints ───
try:
    from backend.routes.resume_routes import resume_bp
    from backend.routes.track_routes import track_bp
    
    logger.info("[APP] resume_bp type:")
    logger.info(f"         {type(resume_bp)}")

    app.register_blueprint(resume_bp, url_prefix="/api")
    app.register_blueprint(track_bp, url_prefix="/api")
    logger.info("[OK] Registered resume routes")
    
    # Debug: Print all registered routes
    logger.info("[APP] === ALL REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        logger.info(f"    {rule.rule} -> {rule.endpoint}")
except Exception as e:
    logger.error(f"[ERR] Failed to register resume routes: {e}")
    import traceback
    logger.error(traceback.format_exc())

# Clean up stale temp PDFs from previous sessions
try:
    from backend.config import get_temp_dir
    from pathlib import Path
    import time
    temp_dir = get_temp_dir()
    now = time.time()
    cleaned = 0
    for f in Path(temp_dir).iterdir():
        if f.is_file() and f.suffix == '.pdf':
            # Remove temp files older than 1 hour
            if now - f.stat().st_mtime > 3600:
                f.unlink(missing_ok=True)
                cleaned += 1
    if cleaned:
        logger.info(f"[OK] Cleaned {cleaned} stale temp PDF(s) from {temp_dir}")
except Exception as e:
    logger.warning(f"[WARN] Failed to clean temp PDFs: {e}")

# ─── Serve Web Frontend ───
# Try multiple locations: source tree (dev), installed package, editable install
def _find_web_dist():
    # 0. PyInstaller frozen bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        meipass_dist = Path(sys._MEIPASS) / "web" / "dist"
        if meipass_dist.exists():
            return meipass_dist
    # 1. Installed package data (pip install)
    try:
        import web as web_pkg
        pkg_dist = Path(web_pkg.__file__).parent / "dist"
        if pkg_dist.exists():
            return pkg_dist
    except (ImportError, AttributeError):
        pass
    # 2. Source tree (dev / pip install -e .)
    src_dist = Path(__file__).parent.parent / "web" / "dist"
    if src_dist.exists():
        return src_dist
    # 3. Backend package sibling (some build setups)
    sibling_dist = Path(__file__).parent / "web" / "dist"
    if sibling_dist.exists():
        return sibling_dist
    return None

web_dist = _find_web_dist()
if web_dist is not None:
    logger.info(f"[APP] Serving web frontend from: {web_dist}")

    @app.route("/")
    def index():
        return send_from_directory(str(web_dist), "index.html")

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(str(web_dist / "assets"), filename)

    @app.route("/<path:filename>")
    def serve_static(filename):
        file_path = web_dist / filename
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(web_dist), filename)
        return send_from_directory(str(web_dist), "index.html")
else:
    logger.info("[APP] Web frontend not built yet. Run 'npm run build' in web/ directory.")


# ─── Error Handlers ───
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": "Bad request"}), 400


@app.errorhandler(404)
def not_found(error):
    logger.error(f"[ERR] 404 NOT FOUND: {request.path} - {error}")
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"[ERR] SERVER ERROR HANDLER: {error}")
    import traceback
    logger.error(f"[ERR] Traceback: {traceback.format_exc()}")
    return jsonify({"success": False, "error": "Internal server error"}), 500


# ─── Startup & Shutdown Handlers ───
def startup_ollama():
    """Initialize Ollama service on app startup."""
    logger.info("=" * 60)
    logger.info("[APP] Initializing Ollama LLM Service...")
    logger.info("=" * 60)

    if ollama_service.startup():
        logger.info("[OK] Ollama service initialized successfully!")
    else:
        logger.warning("[WARN] Ollama service failed to initialize. Please ensure Ollama is installed and running: https://ollama.ai")


def shutdown_ollama():
    """Gracefully shutdown Ollama service on app shutdown."""
    logger.info("=" * 60)
    logger.info("[APP] Shutting down Ollama LLM Service...")
    logger.info("=" * 60)
    ollama_service.shutdown()
    logger.info("[OK] Ollama service shutdown complete")


# ─── Startup ───
if __name__ == "__main__":
    logger.info("[APP] Starting Resume AI Backend on")
    logger.info(f"    {FLASK_HOST}:{FLASK_PORT}")

    # Initialize Ollama on startup
    startup_ollama()

    # Register shutdown handler
    atexit.register(shutdown_ollama)

    try:
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("[OK] Shutdown signal received")
    finally:
        shutdown_ollama()