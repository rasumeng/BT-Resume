"""
Flask Backend for Resume AI - Local AI Service Layer
Manages all resume processing and API endpoints.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add core module to path
core_path = Path(__file__).parent.parent / "core"
sys.path.insert(0, str(core_path))

from config import FLASK_HOST, FLASK_PORT, OLLAMA_HOST, get_resumes_dir

# ─── Setup Logging ───
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Flask App Setup ───
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ─── Health Check Endpoint (Critical for Startup) ───
@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint - used by Flutter to verify backend is ready.
    This should be the FIRST thing Flutter checks when launching.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "resume-ai-api"
    })

# ─── Register Route Blueprints ───
try:
    from routes.resume_routes import resume_bp
    app.register_blueprint(resume_bp, url_prefix='/api')
    logger.info("✓ Registered resume routes")
except Exception as e:
    logger.error(f"✗ Failed to register resume routes: {e}")

# ─── Error Handlers ───
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"success": False, "error": "Internal server error"}), 500

# ─── Startup ───
if __name__ == '__main__':
    logger.info(f"🚀 Starting Resume AI Backend on {FLASK_HOST}:{FLASK_PORT}")
    logger.info(f"📁 Resumes directory: {get_resumes_dir()}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
