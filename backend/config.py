"""
Backend configuration for BT-Resume.
Handles ports, paths, environment setup, and secret key management.

All settings can be overridden via environment variables.
"""

import os
import platform
import secrets
from pathlib import Path

# ─── Flask Configuration (env var overrides) ───
FLASK_HOST = os.environ.get("BT_RESUME_HOST", "127.0.0.1")
FLASK_PORT = int(os.environ.get("BT_RESUME_PORT", "5000"))
FLASK_DEBUG = os.environ.get("BT_RESUME_DEBUG", "false").lower() == "true"

# ─── Ollama Configuration ───
OLLAMA_HOST = os.environ.get("BT_RESUME_OLLAMA_HOST", "http://localhost:11434")

# ─── Tracking / Analytics ───
ENABLE_ANALYTICS = os.environ.get("BT_RESUME_ENABLE_ANALYTICS", "true").lower() == "true"

# ─── Paths (defined before SECRET_KEY since _load_or_generate_secret_key calls get_app_data_dir) ───
def get_app_data_dir():
    r"""Get the user's app data directory (platform-specific).
    Windows: C:\Users\<User>\Documents\BT-Resume
    macOS: ~/Documents/BT-Resume
    Linux: ~/.local/share/BT-Resume
    """
    if platform.system() == "Windows":
        user_home = Path(os.path.expanduser("~"))
        app_data = user_home / "Documents" / "BT-Resume"
    elif platform.system() == "Darwin":
        user_home = Path(os.path.expanduser("~"))
        app_data = user_home / "Documents" / "BT-Resume"
    else:
        user_home = Path(os.path.expanduser("~"))
        app_data = user_home / ".local" / "share" / "BT-Resume"

    app_data.mkdir(parents=True, exist_ok=True)
    return app_data

def get_base_dir():
    """Get the base directory of the project."""
    return Path(__file__).parent.parent

def get_resumes_dir():
    """Get the resumes directory in user's app data."""
    app_data = get_app_data_dir()
    resumes_dir = app_data / "resumes"
    resumes_dir.mkdir(parents=True, exist_ok=True)
    return resumes_dir

def get_outputs_dir():
    """Get the outputs directory in user's app data."""
    app_data = get_app_data_dir()
    outputs_dir = app_data / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    return outputs_dir

def get_temp_dir():
    """Get the temp directory for auto-generated PDF previews (polished/tailored).

    These files are disposable and cleaned up on backend restart.
    """
    app_data = get_app_data_dir()
    temp_dir = app_data / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir

# ─── Secret Key ───
def _load_or_generate_secret_key() -> str:
    """Load secret key from app data dir, or generate and persist a new one."""
    secret_file = get_app_data_dir() / ".secret_key"
    if secret_file.exists():
        return secret_file.read_text().strip()
    key = secrets.token_hex(32)
    secret_file.write_text(key)
    return key

SECRET_KEY = _load_or_generate_secret_key()

# ─── Models ───
MODELS = {
    "polish": "mistral:7b",
    "tailor": "mistral:7b",
    "grade": "mistral:7b",
    "parse": "mistral:7b",
}

# ─── Response Schema Defaults ───
DEFAULT_RESPONSE = {
    "success": True,
    "data": None,
    "error": None,
    "timestamp": None
}
