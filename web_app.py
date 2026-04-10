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
import base64
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

try:
    import fitz  # PyMuPDF
    PDFS_AVAILABLE = True
except ImportError:
    PDFS_AVAILABLE = False
    print("WARNING: PyMuPDF not installed. PDF preview will not work.")

# ═══════════════════════════════════════════════════════════════
# FLASK APP SETUP
# ═══════════════════════════════════════════════════════════════

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create resumes folder if it doesn't exist
RESUMES_FOLDER = os.path.join(os.path.dirname(__file__), 'resumes')
os.makedirs(RESUMES_FOLDER, exist_ok=True)

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


@app.route('/api/list-resumes', methods=['GET'])
def list_resumes():
    """List all saved resumes in the resumes folder"""
    try:
        resumes = []
        for filename in os.listdir(RESUMES_FOLDER):
            if filename.endswith(('.pdf', '.txt', '.json')):
                filepath = os.path.join(RESUMES_FOLDER, filename)
                file_size = os.path.getsize(filepath)
                mod_time = os.path.getmtime(filepath)
                resumes.append({
                    "name": filename,
                    "size": file_size,
                    "modified": mod_time
                })
        
        # Sort by modified time (most recent first)
        resumes.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            "status": "success",
            "resumes": resumes
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/get-resume', methods=['GET'])
def get_resume():
    """
    Serve the actual resume file (PDF or TXT)
    
    Query Parameters:
        - filename: Resume filename
    
    Returns:
        - The file itself (application/pdf or text/plain)
    """
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Resume not found"}), 404
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext == '.pdf':
            return send_file(filepath, mimetype='application/pdf')
        elif file_ext == '.txt':
            return send_file(filepath, mimetype='text/plain')
        else:
            return jsonify({"error": "Unsupported file type"}), 400
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/load-resume', methods=['POST'])
def load_resume():
    """Load and parse a saved resume"""
    try:
        data = request.json or {}
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Resume not found"}), 404
        
        # Check if it's a cached JSON version
        json_path = filepath + '.json'
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                sections = json.load(f)
        else:
            # Parse the resume
            sections = parse_resume_with_mistral(filepath)
            
            # Cache the parsed sections
            with open(json_path, 'w') as f:
                json.dump(sections, f)
        
        if sections is None:
            return jsonify({"error": "Failed to parse resume"}), 500
        
        # Store in session
        session_id = os.urandom(16).hex()
        sessions[session_id] = {
            "sections": sections,
            "resume_file": filepath,
            "filename": filename
        }
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "filename": filename,
            "sections": sections
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    """
    Save a resume file (PDF or TXT) to resumes folder WITHOUT parsing
    
    Request:
        - file: Resume file (multipart/form-data)
    
    Response:
        - filename: Saved filename
        - status: success
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File must be PDF or TXT"}), 400
        
        # Save resume to resumes folder (just save, don't parse)
        filename = secure_filename(file.filename)
        filepath = os.path.join(RESUMES_FOLDER, filename)
        file.save(filepath)
        
        return jsonify({
            "status": "success",
            "filename": filename
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/preview-resume', methods=['GET'])
def preview_resume():
    """
    Generate a preview image of the resume (first page if PDF, or text preview if TXT)
    
    Query Parameters:
        - filename: Resume filename
    
    Response:
        - preview_type: 'image' or 'text'
        - preview_data: Base64 encoded image or plain text
        - error: Error message if failed
    """
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({"error": "Resume not found"}), 404
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        # PDF preview - convert first page to image using PyMuPDF
        if file_ext == '.pdf' and PDFS_AVAILABLE:
            try:
                pdf_doc = fitz.open(filepath)
                if pdf_doc.page_count > 0:
                    page = pdf_doc[0]  # Get first page
                    # Render page to image at 150 DPI
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                    img_data = pix.tobytes("png")
                    img_base64 = base64.b64encode(img_data).decode()
                    pdf_doc.close()
                    
                    return jsonify({
                        "status": "success",
                        "preview_type": "image",
                        "preview_data": f"data:image/png;base64,{img_base64}"
                    })
            except Exception as e:
                print(f"Error converting PDF to image: {e}")
                # Fallback to text preview if PDF conversion fails
                pass
        
        # Text preview - for TXT files or PDF fallback
        if file_ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()[:2000]  # First 2000 chars
            
            return jsonify({
                "status": "success",
                "preview_type": "text",
                "preview_data": text
            })
        
        # If PDF but no pdf2image, return message
        if file_ext == '.pdf':
            return jsonify({
                "status": "success",
                "preview_type": "text",
                "preview_data": "[PDF file - install pdf2image to see visual preview]\n\nUse the Grade Resume feature to parse the content."
            })
        
        return jsonify({"error": "Unsupported file type"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/parse-resume-lazy', methods=['POST'])
def parse_resume_lazy():
    """
    Parse a resume on-demand (lazy parsing)
    
    Request:
        - filename: Resume filename to parse
    
    Response:
        - sections: Parsed resume structure
        - session_id: Session ID for future operations
    """
    try:
        data = request.json or {}
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        if not os.path.exists(filepath):
            return jsonify({"error": "Resume not found"}), 404
        
        # Check if already parsed and cached
        json_path = filepath + '.json'
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                sections = json.load(f)
        else:
            # Parse resume for first time
            sections = parse_resume_with_mistral(filepath)
            
            if sections is None:
                return jsonify({"error": "Failed to parse resume"}), 500
            
            # Cache the parsed sections
            with open(json_path, 'w') as f:
                json.dump(sections, f)
        
        # Store in session
        session_id = os.urandom(16).hex()
        sessions[session_id] = {
            "sections": sections,
            "resume_file": filepath,
            "filename": filename
        }
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "filename": filename,
            "sections": sections
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500



@app.route('/api/grade-resume', methods=['POST'])
def grade_resume():
    """
    Grade a resume (parses on-demand if needed)
    
    Request:
        - filename: Resume filename OR
        - resume_text: Plain text resume
    
    Response:
        - scores: Overall, ATS, sections, bullets, keywords scores
    """
    try:
        data = request.json or {}
        filename = data.get('filename')
        resume_text = data.get('resume_text')
        
        # Parse on-demand if filename provided
        if filename and not resume_text:
            filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
            if not os.path.exists(filepath):
                return jsonify({"error": "Resume not found"}), 400
            
            # Check cache first
            json_path = filepath + '.json'
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    sections = json.load(f)
            else:
                sections = parse_resume_with_mistral(filepath)
                if sections is None:
                    return jsonify({"error": "Failed to parse resume"}), 500
                # Cache it
                with open(json_path, 'w') as f:
                    json.dump(sections, f)
            
            resume_text = _sections_to_text(sections)
        elif not resume_text:
            return jsonify({"error": "Resume file or text required"}), 400
        
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
        - filename: Resume filename (will parse on-demand) OR
        - resume_text: Plain text resume
        - job_description: Job posting text
    
    Response:
        - tailored_resume: Resume data tailored to job
    """
    try:
        data = request.json or {}
        
        filename = data.get('filename')
        resume_text = data.get('resume_text')
        job_description = data.get('job_description')
        
        if not job_description:
            return jsonify({"error": "Job description required"}), 400
        
        # Get resume from filename (lazy parse) or use provided text
        if filename:
            filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
            if not os.path.exists(filepath):
                return jsonify({"error": "Resume not found"}), 404
            
            # Check cache first
            json_path = filepath + '.json'
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    sections = json.load(f)
            else:
                sections = parse_resume_with_mistral(filepath)
                if sections is None:
                    return jsonify({"error": "Failed to parse resume"}), 500
                # Cache it
                with open(json_path, 'w') as f:
                    json.dump(sections, f)
        elif resume_text:
            # Parse the provided text
            sections = _text_to_sections(resume_text)
        else:
            return jsonify({"error": "Resume file or text required"}), 400
        
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
        - filename: Resume filename (will parse on-demand) OR
        - resume_text: Plain text resume
    
    Response:
        - PDF file
    """
    try:
        data = request.json or {}
        
        filename = data.get('filename')
        resume_text = data.get('resume_text')
        
        # Get resume from filename (lazy parse) or use provided text
        if filename:
            filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
            if not os.path.exists(filepath):
                return jsonify({"error": "Resume not found"}), 404
            
            # Check cache first
            json_path = filepath + '.json'
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    sections = json.load(f)
            else:
                sections = parse_resume_with_mistral(filepath)
                if sections is None:
                    return jsonify({"error": "Failed to parse resume"}), 500
                # Cache it
                with open(json_path, 'w') as f:
                    json.dump(sections, f)
        elif resume_text:
            sections = _text_to_sections(resume_text)
        else:
            return jsonify({"error": "Resume file or text required"}), 400
        
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
