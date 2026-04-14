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

from core.input_parser import parse_resume_with_mistral, load_text, load_pdf
from core.output_builder import build_resume, clean_bullets
from core.pdf_generator import generate_pdf
from core.resume_grader import ResumeGrader
from core.prompts import (
    bullet_polish_prompt,
    job_tailor_prompt,
    experience_updater_prompt,
    resume_polish_prompt,
    get_changes_summary_prompt
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


@app.route('/api/model-status', methods=['GET'])
def model_status():
    """
    Check status of Ollama and which models are loaded
    
    Returns:
        - running: Whether Ollama server is running
        - available_models: List of loaded models
        - missing_models: List of models that should be loaded but aren't
        - loaded: Whether all required models are loaded
    """
    try:
        from core.llm_client import ensure_models_loaded
        status = ensure_models_loaded()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "status": "error"
        }), 500


@app.route('/api/pull-model', methods=['POST'])
def pull_model_endpoint():
    """
    Pull (download and load) a specific model
    
    Request:
        - model: Model name (e.g., "mistral:7b", "llama3:8b")
    
    Returns:
        - success: Whether the pull was successful
        - message: Status message
    """
    try:
        data = request.json or {}
        model = data.get('model')
        
        if not model:
            return jsonify({"error": "Model name required"}), 400
        
        from core.llm_client import pull_model
        success = pull_model(model)
        
        return jsonify({
            "success": success,
            "model": model,
            "message": f"{'Successfully pulled' if success else 'Failed to pull'} model {model}"
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/resume-status', methods=['GET'])
def resume_status():
    """
    Check if a resume has been parsed and cached
    
    Query Parameters:
        - filename: Resume filename to check
    
    Returns:
        - filename: The resume filename
        - exists: Whether the resume file exists
        - parsed: Whether the JSON cache exists (resume has been parsed)
        - cache_file: Path to the cache file if it exists
        - cache_time: When the cache was created (unix timestamp)
    """
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        json_path = filepath + '.json'
        
        exists = os.path.exists(filepath)
        parsed = os.path.exists(json_path)
        cache_time = None
        
        if parsed:
            cache_time = os.path.getmtime(json_path)
        
        return jsonify({
            "filename": filename,
            "exists": exists,
            "parsed": parsed,
            "cache_file": json_path if parsed else None,
            "cache_time": cache_time
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


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


@app.route('/api/resumes-folder-info', methods=['GET'])
def resumes_folder_info():
    """
    Get information about the resumes storage folder
    
    Returns:
        - folder_path: Absolute path to the resumes folder
        - folder_path_display: User-friendly display path
        - file_count: Number of resume files (excluding JSON cache files)
        - total_size: Total size of all resumes in bytes
        - total_size_mb: Total size in megabytes
        - files: List of all files with their details
    """
    try:
        import platform
        
        file_list = []
        total_size = 0
        file_count = 0
        
        for filename in os.listdir(RESUMES_FOLDER):
            filepath = os.path.join(RESUMES_FOLDER, filename)
            
            # Only count actual resume files, not JSON caches
            if filename.endswith(('.pdf', '.txt')):
                file_count += 1
                file_size = os.path.getsize(filepath)
                total_size += file_size
                mod_time = os.path.getmtime(filepath)
                
                file_list.append({
                    "name": filename,
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2),
                    "modified_time": mod_time,
                    "type": "pdf" if filename.endswith('.pdf') else "txt"
                })
        
        # Sort by name
        file_list.sort(key=lambda x: x['name'])
        
        return jsonify({
            "status": "success",
            "folder_path": RESUMES_FOLDER,
            "folder_path_display": RESUMES_FOLDER.replace("\\", "/"),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": file_list,
            "os": platform.system()
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/open-resumes-folder', methods=['POST'])
def open_resumes_folder():
    """
    Open the resumes folder in the system file explorer (Windows/Mac/Linux)
    
    Returns:
        - success: Whether the folder was opened
        - message: Status message
        - folder_path: The folder path that was opened
    """
    try:
        import subprocess
        import platform
        
        # Normalize path for display
        folder_path = os.path.abspath(RESUMES_FOLDER)
        
        system = platform.system()
        
        if system == 'Windows':
            # Open folder in Windows Explorer
            subprocess.Popen(f'explorer "{folder_path}"')
        elif system == 'Darwin':
            # Open folder in Finder (macOS)
            subprocess.Popen(['open', folder_path])
        else:
            # Open folder in file manager (Linux)
            subprocess.Popen(['xdg-open', folder_path])
        
        return jsonify({
            "success": True,
            "message": f"Opened resumes folder in {system} file explorer",
            "folder_path": folder_path
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Could not open folder: {str(e)}",
            "folder_path": os.path.abspath(RESUMES_FOLDER)
        }), 500


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


@app.route('/api/get-resume-text', methods=['GET'])
def get_resume_text():
    """
    Extract text content from a resume file (PDF or TXT)
    
    Query Parameters:
        - filename: Resume filename
    
    Returns:
        JSON with extracted text content
    """
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Resume not found"}), 404
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if file_ext == '.pdf':
                text_content = load_pdf(filepath)
            elif file_ext == '.txt':
                text_content = load_text(filepath)
            else:
                return jsonify({"error": "Unsupported file type"}), 400
            
            return jsonify({"content": text_content, "filename": filename}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to extract text: {str(e)}"}), 500
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/delete-resume', methods=['DELETE'])
def delete_resume():
    """
    Delete a resume file from disk
    
    Query Parameters:
        - filename: Resume filename to delete
    
    Response:
        - status: success or error
    """
    try:
        filename = request.args.get('filename')
        if not filename:
            return jsonify({"error": "Filename required"}), 400
        
        filepath = os.path.join(RESUMES_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Resume not found"}), 404
        
        # Delete the main file
        os.remove(filepath)
        
        # Also delete cached JSON version if it exists
        json_path = filepath + '.json'
        if os.path.exists(json_path):
            os.remove(json_path)
        
        return jsonify({
            "status": "success",
            "message": f"Resume '{filename}' deleted successfully"
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/save-resume-pdf', methods=['POST'])
def save_resume_pdf():
    """
    Save resume content as a PDF file
    
    Request:
        - filename: Desired PDF filename (without extension)
        - resume_text: Plain text resume content
    
    Response:
        - filename: Saved filename (with .pdf extension)
        - status: success or error
    """
    try:
        data = request.json or {}
        filename = data.get('filename')
        resume_text = data.get('resume_text')
        
        if not filename or not filename.strip():
            return jsonify({"error": "Filename required"}), 400
        
        if not resume_text or not resume_text.strip():
            return jsonify({"error": "Resume content required"}), 400
        
        # Sanitize filename and ensure .pdf extension
        clean_filename = secure_filename(filename.strip())
        if not clean_filename.endswith('.pdf'):
            clean_filename = clean_filename + '.pdf'
        
        # Check if file already exists
        filepath = os.path.join(RESUMES_FOLDER, clean_filename)
        if os.path.exists(filepath):
            return jsonify({"error": "File already exists"}), 400
        
        print(f"\n{'='*60}")
        print(f"💾 SAVING RESUME AS PDF: {clean_filename}")
        print(f"{'='*60}")
        
        # Write text to temp file with explicit UTF-8 encoding
        temp_txt = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        temp_txt.write(resume_text)
        temp_txt.close()
        print(f"✓ Temp file created: {temp_txt.name}")
        
        try:
            # Parse the resume properly with Mistral
            print(f"🤖 Parsing resume with LLM...")
            sections = parse_resume_with_mistral(temp_txt.name)
            if sections is None:
                raise Exception("Failed to parse resume - Mistral returned None")
            print(f"✓ Successfully parsed into {len(sections)} sections")
            
            # Generate PDF from parsed sections
            print(f"📄 Generating PDF file...")
            generate_pdf(sections, filepath)
            print(f"✓ PDF generated: {filepath}")
            
            # Cache the parsed sections
            json_path = filepath + '.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(sections, f, ensure_ascii=False, indent=2)
            print(f"✓ Sections cached to JSON")
            
            print(f"✅ Resume saved successfully as {clean_filename}\n")
            return jsonify({
                "status": "success",
                "filename": clean_filename,
                "message": f"Resume saved as PDF: {clean_filename}"
            })
        finally:
            # Clean up temp file
            if os.path.exists(temp_txt.name):
                os.remove(temp_txt.name)
                print(f"✓ Temp file cleaned up")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
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
            
            print(f"\n🔍 Grading request for: {filename}")
            
            # Check cache first
            json_path = filepath + '.json'
            if os.path.exists(json_path):
                print(f"✓ Found cached JSON for {filename}")
                with open(json_path, 'r') as f:
                    sections = json.load(f)
            else:
                print(f"⏳ No cache found, parsing resume...")
                try:
                    sections = parse_resume_with_mistral(filepath)
                except Exception as parse_error:
                    error_msg = str(parse_error)
                    print(f"❌ Parsing failed: {error_msg}")
                    return jsonify({"error": f"Failed to parse resume: {error_msg}"}), 500
                if sections is None:
                    return jsonify({"error": "Failed to parse resume (no sections returned)"}), 500
                # Cache it
                print(f"💾 Caching parsed resume to {json_path}")
                with open(json_path, 'w') as f:
                    json.dump(sections, f)
            
            resume_text = _sections_to_text(sections)
        elif not resume_text:
            return jsonify({"error": "Resume file or text required"}), 400
        
        grader = ResumeGrader()
        try:
            print(f"🤖 Sending to grader (Mistral:7b)...")
            scores = grader.grade(resume_text)
        except Exception as grade_error:
            # Re-raise to be caught by outer exception handler
            raise grade_error
        
        if scores is None:
            print(f"❌ Grader returned no scores")
            return jsonify({"error": "Failed to grade resume (no scores returned)"}), 500
        
        print(f"✓ Grading complete - Overall score: {scores.get('overall', 'N/A')}")
        return jsonify({
            "status": "success",
            "scores": scores
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"Grade resume error: {error_msg}")
        return jsonify({"error": error_msg}), 500



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


@app.route('/api/polish-resume', methods=['POST'])
def polish_resume():
    """
    Polish an entire resume - enhance wording, verb precision, and structure
    
    Request:
        - resume_content: Full resume text (string)
        - intensity: Polishing intensity level (light, medium, aggressive) - default: medium
    
    Response:
        - polished_resume: Enhanced resume text
        - changes: Array of specific improvements made (up to 8)
        - success: Boolean indicating success
    """
    try:
        data = request.json or {}
        resume_content = data.get('resume_content')
        intensity = data.get('intensity', 'medium')
        
        # Validate intensity
        valid_intensities = ['light', 'medium', 'aggressive']
        if intensity not in valid_intensities:
            intensity = 'medium'
        
        if not resume_content or not resume_content.strip():
            return jsonify({
                "error": "Resume content is required",
                "success": False
            }), 400
        
        # Polish the entire resume with selected intensity
        prompt = resume_polish_prompt(resume_content, mode=intensity)
        polished_resume = ask_llm(prompt, task_type="polish")
        
        if not polished_resume:
            return jsonify({
                "error": "Failed to polish resume",
                "success": False
            }), 500
        
        # Generate a summary of changes made
        changes_prompt = get_changes_summary_prompt(resume_content, polished_resume)
        changes_response = ask_llm(changes_prompt, task_type="analyze")
        
        changes = []
        if changes_response:
            try:
                # Try to parse JSON response
                import json as json_lib
                # Extract JSON array from response
                json_str = changes_response.strip()
                if json_str.startswith('['):
                    changes = json_lib.loads(json_str)
                else:
                    # If not valid JSON, use response as single change
                    changes = [changes_response.strip()]
            except:
                # If parsing fails, create a generic change message
                changes = ["Resume was enhanced with improved wording and professional language"]
        
        # Ensure we have an array and limit to 8 changes
        if not isinstance(changes, list):
            changes = [str(changes)] if changes else []
        changes = changes[:8]
        
        return jsonify({
            "status": "success",
            "success": True,
            "polished_resume": polished_resume.strip(),
            "changes": changes
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "success": False
        }), 500


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
