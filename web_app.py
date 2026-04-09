"""
Flask web backend for Resume AI
Exposes core functionality as REST API endpoints
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
import json
from io import BytesIO

from core.input_parser import parse_resume_with_mistral, load_text
from core.output_builder import build_resume, clean_bullets
from core.pdf_generator import generate_pdf
from core.resume_grader import ResumeGrader
from core.prompts import (
    bullet_polish_prompt,
    job_tailor_prompt,
    experience_updater_prompt
)
from core.llm_client import ask_llm

# ═══════════════════════════════════════════════════════════════
# FLASK APP SETUP
# ═══════════════════════════════════════════════════════════════

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Store session data
sessions = {}

# ═══════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/', methods=['GET'])
def index():
    """Serve the main UI"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Resume AI backend is running"})


@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """
    Parse a resume file (PDF or TXT)
    
    Request:
        - file: Resume file (multipart/form-data)
    
    Response:
        - sections: Parsed resume structure
        - session_id: Session ID for future operations
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File must be PDF or TXT"}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Parse resume
        sections = parse_resume_with_mistral(filepath)
        
        if sections is None:
            return jsonify({"error": "Failed to parse resume"}), 500
        
        # Store in session
        session_id = os.urandom(16).hex()
        sessions[session_id] = {
            "sections": sections,
            "resume_file": filepath
        }
        
        # Clean up
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "sections": sections
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/grade-resume', methods=['POST'])
def grade_resume():
    """
    Grade a resume (can be text or from parsed sections)
    
    Request:
        - resume_text: Plain text resume (OR)
        - session_id: Session ID with parsed sections
    
    Response:
        - scores: Overall, ATS, sections, bullets, keywords scores
    """
    try:
        data = request.json or {}
        
        resume_text = data.get('resume_text')
        session_id = data.get('session_id')
        
        if session_id and session_id in sessions:
            # Convert parsed sections back to text for grading
            sections = sessions[session_id]["sections"]
            resume_text = _sections_to_text(sections)
        elif not resume_text:
            return jsonify({"error": "Resume text or session_id required"}), 400
        
        grader = ResumeGrader()
        scores = grader.grade(resume_text)
        
        if scores is None:
            return jsonify({"error": "Failed to grade resume"}), 500
        
        return jsonify({
            "status": "success",
            "scores": scores
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/polish-bullets', methods=['POST'])
def polish_bullets():
    """
    Polish resume bullets using Llama3
    
    Request:
        - bullets: Array of bullet points OR single bullet string
    
    Response:
        - polished_bullets: Improved bullet points
    """
    try:
        data = request.json or {}
        bullets = data.get('bullets')
        
        if not bullets:
            return jsonify({"error": "Bullets required"}), 400
        
        # Handle both single string and array
        if isinstance(bullets, str):
            bullets = [bullets]
        
        polished = []
        for bullet in bullets:
            prompt = bullet_polish_prompt(bullet)
            result = ask_llm(prompt, task_type="polish")
            if result:
                polished.append(result.strip())
        
        return jsonify({
            "status": "success",
            "polished_bullets": polished
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/tailor-resume', methods=['POST'])
def tailor_resume():
    """
    Tailor resume to a specific job posting
    
    Request:
        - session_id: Session with parsed resume (OR)
        - resume_text: Plain text resume
        - job_description: Job posting text
    
    Response:
        - tailored_resume: Resume data tailored to job
    """
    try:
        data = request.json or {}
        
        session_id = data.get('session_id')
        resume_text = data.get('resume_text')
        job_description = data.get('job_description')
        
        if not job_description:
            return jsonify({"error": "Job description required"}), 400
        
        # Get resume from session or use provided text
        if session_id and session_id in sessions:
            sections = sessions[session_id]["sections"]
        elif resume_text:
            # Parse the provided text
            sections = _text_to_sections(resume_text)
        else:
            return jsonify({"error": "Resume data or session_id required"}), 400
        
        # Build tailored resume
        resume_data = build_resume(sections, job_description)
        
        return jsonify({
            "status": "success",
            "tailored_resume": resume_data
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/update-experience', methods=['POST'])
def update_experience():
    """
    Generate polished bullet points for new experience
    
    Request:
        - description: User's experience description
    
    Response:
        - bullets: Generated bullet points
    """
    try:
        data = request.json or {}
        description = data.get('description')
        
        if not description:
            return jsonify({"error": "Experience description required"}), 400
        
        prompt = experience_updater_prompt(description)
        result = ask_llm(prompt, task_type="update")
        
        if not result:
            return jsonify({"error": "Failed to generate bullets"}), 500
        
        bullets = clean_bullets(result)
        
        return jsonify({
            "status": "success",
            "bullets": bullets
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_endpoint():
    """
    Generate PDF from resume data
    
    Request:
        - session_id: Session with resume data (OR)
        - resume_text: Plain text resume
    
    Response:
        - PDF file
    """
    try:
        data = request.json or {}
        
        session_id = data.get('session_id')
        resume_text = data.get('resume_text')
        
        # Get resume from session or use provided text
        if session_id and session_id in sessions:
            sections = sessions[session_id]["sections"]
        elif resume_text:
            sections = _text_to_sections(resume_text)
        else:
            return jsonify({"error": "Resume data or session_id required"}), 400
        
        # Generate PDF to BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate
        
        pdf_buffer = BytesIO()
        
        # Use the generate_pdf function but write to buffer
        # For now, we'll write to a temp file and read it back
        import tempfile
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_pdf_path = temp_pdf.name
        temp_pdf.close()
        
        generate_pdf(sections, temp_pdf_path)
        
        with open(temp_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        
        return send_file(
            BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='resume.pdf'
        )
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _sections_to_text(sections):
    """Convert parsed sections back to plain text"""
    text = []
    
    for section_name, content in sections.items():
        text.append(f"\n{section_name.upper()}\n" + "=" * 40)
        
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if 'position' in item:
                        text.append(f"\n{item['position']}")
                        if item.get('company'):
                            text.append(f"  {item['company']}")
                    
                    if 'bullets' in item:
                        for bullet in item['bullets']:
                            if isinstance(bullet, dict):
                                text.append(f"  - {bullet['text']}")
                            else:
                                text.append(f"  - {bullet}")
                else:
                    text.append(f"  - {item}")
        else:
            text.append(str(content))
    
    return "\n".join(text)


def _text_to_sections(resume_text):
    """Convert plain text resume to sections structure (simple fallback)"""
    # This is a simplified version - in production, use parse_resume_with_mistral
    sections = {}
    current_section = None
    
    for line in resume_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Try to detect section headers
        upper_line = line.upper()
        if 'EXPERIENCE' in upper_line or 'WORK' in upper_line:
            current_section = 'work_experience'
            sections[current_section] = []
        elif 'EDUCATION' in upper_line:
            current_section = 'education'
            sections[current_section] = []
        elif 'SKILLS' in upper_line:
            current_section = 'skills'
            sections[current_section] = []
        elif 'PROJECTS' in upper_line:
            current_section = 'projects'
            sections[current_section] = []
        elif current_section and line.startswith('-'):
            sections[current_section].append(line[1:].strip())
    
    return sections


# ═══════════════════════════════════════════════════════════════
# RUN THE APP
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
