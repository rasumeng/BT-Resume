"""
Tracking Routes - Lightweight anonymous usage analytics.
Logs events to a JSONL file for aggregate insights.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import requests
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

track_bp = Blueprint('track', __name__)


def get_track_dir() -> Path:
    """Get or create tracking data directory."""
    track_dir = Path(__file__).parent.parent.parent / "usage"
    track_dir.mkdir(exist_ok=True)
    return track_dir


METRICS_API = 'https://beyondtheframe.vercel.app/api/track'


def log_event(entry: dict) -> None:
    """Append a JSON event line to the usage log."""
    log_file = get_track_dir() / "events.jsonl"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def send_to_redis_metrics(entry: dict) -> None:
    """POST event to the Redis metrics API (mirrors frontend tracking)."""
    try:
        requests.post(
            METRICS_API,
            json={
                "event": entry.get("event", "unknown"),
                "label": entry.get("label"),
                "meta": entry.get("meta"),
            },
            timeout=5,
        )
    except Exception:
        logger.debug("Failed to send metric to Redis API", exc_info=True)


@track_bp.route('/track', methods=['POST'])
def track():
    """
    Log an anonymous usage event.

    Request JSON:
    {
        "event": "page_view|resume_uploaded|polished|tailored|feedback_submitted|error",
        "label": "optional detail (e.g. tab name, intensity)",
        "meta": { ... optional extra data ... }
    }
    """
    data = request.get_json(silent=True) or {}

    entry = {
        "event": data.get("event", "unknown"),
        "label": data.get("label"),
        "meta": data.get("meta"),
        "ts": datetime.utcnow().isoformat(),
    }

    try:
        log_event(entry)
    except Exception as e:
        logger.warning(f"Failed to log event: {e}")
        return jsonify({"success": False, "error": "Failed to log event"}), 500

    send_to_redis_metrics(entry)

    return jsonify({"success": True}), 200
