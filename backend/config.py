"""
Backend configuration for Resume AI.
Handles ports, paths, and environment setup.
"""

import os
import platform
from pathlib import Path

# ─── Flask Configuration ───
FLASK_HOST = "127.0.0.1"  # Only localhost (secure for local app)
FLASK_PORT = 5000
FLASK_DEBUG = False

# ─── Ollama Configuration ───
OLLAMA_HOST = "http://localhost:11434"

# ─── Paths ───
def get_base_dir():
    """Get the base directory of the project."""
    return Path(__file__).parent.parent

def get_resumes_dir():
    """Get the resumes directory."""
    base_dir = get_base_dir()
    resumes_dir = base_dir / "resumes"
    resumes_dir.mkdir(exist_ok=True)
    return resumes_dir

def get_outputs_dir():
    """Get the outputs directory."""
    base_dir = get_base_dir()
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    return outputs_dir

def get_models_dir():
    """Get the models directory."""
    base_dir = get_base_dir()
    models_dir = base_dir / "models"
    models_dir.mkdir(exist_ok=True)
    return models_dir

# ─── Models ───
MODELS = {
    "polish": "mistral:7b",      # Fast, good for bullet polish
    "tailor": "llama2:7b-chat",  # Stronger instruction following for job matching
}

# ─── Response Schema Defaults ───
DEFAULT_RESPONSE = {
    "success": True,
    "data": None,
    "error": None,
    "timestamp": None
}
