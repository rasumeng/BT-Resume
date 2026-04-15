"""
Resume Routes - HTTP endpoints for resume operations.
Clean separation: routes handle HTTP, services handle business logic.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

from services.file_service import FileService
from services.llm_service import LLMService

# Create blueprint
resume_bp = Blueprint('resume', __name__)

# ─────────────────────────────────────────────────────────────
# FILE OPERATIONS
# ─────────────────────────────────────────────────────────────

@resume_bp.route('/list-resumes', methods=['GET'])
def list_resumes():
    """List all resumes in the folder."""
    result = FileService.list_resumes()
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/get-resume', methods=['GET'])
def get_resume():
    """Get resume content by filename."""
    filename = request.args.get('filename')
    
    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400
    
    result = FileService.get_resume(filename)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/update-resume', methods=['POST'])
def update_resume():
    """Update an existing resume."""
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    
    if not filename or content is None:
        return jsonify({"success": False, "error": "filename and content required"}), 400
    
    result = FileService.update_resume(filename, content)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/save-resume-pdf', methods=['POST'])
def save_resume_pdf():
    """Generate and save a PDF resume."""
    data = request.get_json()
    filename = data.get('filename')
    resume_text = data.get('resume_text')
    
    if not filename or not resume_text:
        return jsonify({"success": False, "error": "filename and resume_text required"}), 400
    
    # Ensure .pdf extension
    if not filename.endswith('.pdf'):
        filename = filename.replace('.txt', '') + '.pdf'
    
    result = FileService.save_resume_pdf(filename, resume_text)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/delete-resume', methods=['DELETE'])
def delete_resume():
    """Delete a resume file."""
    filename = request.args.get('filename')
    
    if not filename:
        return jsonify({"success": False, "error": "filename required"}), 400
    
    result = FileService.delete_resume(filename)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
# LLM OPERATIONS (AI processing)
# ─────────────────────────────────────────────────────────────

@resume_bp.route('/polish-bullets', methods=['POST'])
def polish_bullets():
    """
    Polish resume bullets.
    
    Request JSON:
    {
        "bullets": ["bullet 1", "bullet 2", ...],
        "intensity": "light|medium|heavy"
    }
    """
    data = request.get_json()
    bullets = data.get('bullets', [])
    intensity = data.get('intensity', 'medium')
    
    if not isinstance(bullets, list) or len(bullets) == 0:
        return jsonify({"success": False, "error": "bullets array required"}), 400
    
    result = LLMService.polish_bullets(bullets, intensity)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/tailor-resume', methods=['POST'])
def tailor_resume():
    """
    Tailor a resume to a job description.
    
    Request JSON:
    {
        "resume_text": "...",
        "job_description": "..."
    }
    """
    data = request.get_json()
    resume_text = data.get('resume_text')
    job_description = data.get('job_description')
    
    if not resume_text or not job_description:
        return jsonify({"success": False, "error": "resume_text and job_description required"}), 400
    
    result = LLMService.tailor_resume(resume_text, job_description)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/grade-resume', methods=['POST'])
def grade_resume():
    """
    Grade a resume and provide feedback.
    
    Request JSON:
    {
        "resume_text": "..."
    }
    """
    data = request.get_json()
    resume_text = data.get('resume_text')
    
    if not resume_text:
        return jsonify({"success": False, "error": "resume_text required"}), 400
    
    result = LLMService.grade_resume(resume_text)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

@resume_bp.route('/parse-resume', methods=['POST'])
def parse_resume():
    """
    Parse resume text into structured PDF format.
    
    Request JSON:
    {
        "resume_text": "..."
    }
    """
    data = request.get_json()
    resume_text = data.get('resume_text')
    
    if not resume_text:
        return jsonify({"success": False, "error": "resume_text required"}), 400
    
    result = LLMService.parse_to_pdf_format(resume_text)
    status_code = 200 if result.get('success') else 500
    return jsonify(result), status_code

# ─────────────────────────────────────────────────────────────
# RESPONSE SCHEMA
# ─────────────────────────────────────────────────────────────

"""
All responses follow this schema:

SUCCESS:
{
    "success": true,
    "data": {...},  # Operation-specific data
    "error": null,
    "timestamp": "2024-01-01T00:00:00Z"
}

ERROR:
{
    "success": false,
    "data": null,
    "error": "Error message",
    "timestamp": "2024-01-01T00:00:00Z"
}
"""

@resume_bp.before_request
def before_request():
    """Add timestamp to all responses."""
    request.start_time = datetime.utcnow()

@resume_bp.after_request
def after_request(response):
    """Add metadata to response."""
    if response.is_json:
        try:
            data = response.get_json()
            if isinstance(data, dict):
                if 'timestamp' not in data:
                    data['timestamp'] = datetime.utcnow().isoformat()
                response.set_data(json.dumps(data))
        except:
            pass
    return response
