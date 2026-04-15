# BT Resume

A free, local AI resume helper that polishes your resume bullets, tailors your resume to job descriptions, and formats new experience — all running privately on your own machine. No API keys, no subscriptions, no data leaving your device.
---

## Why BT Resume?

Most AI resume tools cost money, require an account, or send your personal data to external servers. This is my take on a free alternative — built from scratch in Python, powered by open-source LLMs that run entirely on your device.

---

## Features

- **Bullet Polish** — rewrites weak resume bullets into strong, ATS-optimized ones using proven resume writing formulas
- **Job Tailoring** — aligns your resume language and keywords to match a specific job description without changing your real experience
- **Experience Updater** — describe a new project or role in plain English and get polished, formatted resume bullets back
- **PDF + TXT input** — works with both plain text and real PDF resumes
- **PDF output** — generates a clean, formatted PDF resume ready to send
- **100% offline** — no internet connection required after setup, no API keys, completely free

---

## Tech Stack

| Layer | Tool |
|---|---|
| Backend Language | Python 3.10+ |
| Frontend Framework | Flutter 3.41.6 (Dart 3.11.4) |
| Desktop Target | Windows (10+) |
| LLM Runtime | [Ollama](https://ollama.com) |
| Bullet Polish Model | Mistral 7B (fast, efficient) |
| Job Tailoring Model | LLaMA 3 8B (stronger instruction following) |
| PDF Reading | pdfplumber |
| PDF Generation | ReportLab |
| HTTP Client | Dio (with logging) |
| REST API | Flask with CORS |

> Smart model routing — uses Mistral for simple tasks and LLaMA 3 for complex ones, balancing speed and quality.

---

## Quick Start (Easiest Way)

### For Non-Technical Users: Download the Installer

Download the Windows installer and let it handle everything:

1. **Download** `BTF-Resume-Setup-1.0.exe`
2. **Run** the installer
3. **Follow the setup wizard** (handles backend + dependencies)
4. **Launch the app** from your Desktop

That's it! No command line required, no Python installation needed.

> See [releases page](https://github.com/yourusername/BTF-Resume/releases) for the latest installer.

### For Developers: Manual Setup

Read the section below for step-by-step setup with both backend and Flutter frontend.

---

## Requirements

- Python 3.10+ (if running from source)
- [Ollama](https://ollama.com) installed on your machine
- 8GB+ RAM recommended
- Windows 7+ / Mac / Linux

---

## Setup (From Source)

**1. Clone the repo**
```bash
git clone https://github.com/rasumeng/BTF-Resume.git
cd BTF-Resume
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Install Ollama and pull models**
```bash
# Install Ollama from https://ollama.com
ollama pull mistral
ollama pull llama3
```

**5. Make sure Ollama is running**
```bash
ollama serve
```

---

## Usage

### Desktop GUI (Recommended)

**Start the backend:**
```powershell
cd "C:\Users\asume\OneDrive\Desktop\Important\Projects\BTF-Resume"
.\venv\Scripts\Activate.ps1
python run_backend.py
```

**Launch the Flutter app:**
```powershell
C:\Users\asume\OneDrive\Desktop\Important\Projects\BTF-Resume\flutter_app\build\windows\x64\runner\Release\btf_resume.exe
```

Or for development:
```powershell
cd flutter_app
flutter run -d windows
```

**Available tabs:**
- **My Resumes** — View and manage all your resumes
- **Polish** — Enhance your bullet points with AI
- **Tailor** — Customize resume for specific job descriptions
- **Grade** — Get resume scores and improvement feedback

### Command Line (Legacy)

```bash
python main.py --resume samples/resume.txt
python main.py --resume samples/resume.txt --job samples/job.txt
python main.py --resume samples/resume.pdf --job samples/job.txt --output outputs/my_resume.pdf
```

---

## Project Structure

```
BTF-Resume/
├── flutter_app/                  # Flutter desktop frontend
│   ├── lib/
│   │   ├── screens/
│   │   │   ├── home_screen.dart        # Main navigation with 4 tabs
│   │   │   ├── polish_screen.dart      # Bullet enhancement screen
│   │   │   ├── tailor_screen.dart      # Job customization screen
│   │   │   ├── grade_screen.dart       # Resume grading screen
│   │   │   └── splash_screen.dart      # Backend startup verification
│   │   ├── services/
│   │   │   └── api_service.dart        # HTTP client for Flask API
│   │   ├── models/
│   │   │   └── resume_model.dart       # Data models & serialization
│   │   └── main.dart                   # App entry point
│   ├── windows/                   # Windows build configuration
│   └── pubspec.yaml
│
├── backend/                      # Flask REST API
│   ├── app.py                    # Flask app with CORS
│   ├── routes/
│   │   └── resume_routes.py      # 10 API endpoints
│   └── services/
│       └── resume_service.py     # Resume processing logic
│
├── core/
│   ├── llm_client.py             # Ollama API wrapper with model routing
│   ├── prompts.py                # All prompt templates
│   ├── input_parser.py           # Resume file reader and section parser
│   ├── output_builder.py         # AI pipeline and section assembler
│   └── resume_grader.py          # Resume scoring engine
│
├── samples/
│   ├── resume.txt                # Sample resume input
│   └── job.txt                   # Sample job description
├── outputs/                      # Generated PDFs and backups
├── run_backend.py                # Backend startup script
├── requirements.txt              # Python dependencies
└── README.md
```

---

## Architecture

### Desktop Application Flow
```
Flutter Desktop UI (Windows)
    ↓ (HTTP/JSON)
Flask REST API (localhost:5000)
    ↓
Python Backend Services
    ↓
Ollama Local LLM
    ↓
Resume Output (PDF/TXT)
```

### Resume Processing Pipeline
```
Resume File (.txt or .pdf)
        ↓
  Input Parser — extracts and splits resume into sections
        ↓
  Output Builder — routes each section through the right AI prompt
        ↓
  Ollama (Local LLM) — Mistral 7B or LLaMA 3 8B depending on task
        ↓
  Resume Grader — scores and provides feedback
        ↓
  PDF Generator — assembles and outputs clean resume
        ↓
  Flutter UI — displays results in real-time
```

### API Endpoints (10 total)
- `POST /api/polish-bullets` — Enhance resume bullets
- `POST /api/tailor-resume` — Customize for job description
- `POST /api/grade-resume` — Score and analyze resume
- `GET /api/list-resumes` — List all available resumes
- `GET /api/get-resume/{name}` — Load specific resume
- `PUT /api/update-resume` — Update resume content
- `DELETE /api/delete-resume/{name}` — Remove resume
- `POST /api/parse-resume` — Parse uploaded resume
- `POST /api/save-resume-pdf` — Generate PDF output
- `GET /api/health` — Backend health check

---

## Building the Installer (For Developers)

To create the Windows installer for distribution:

1. **Install build tools:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download and install [Inno Setup](https://jrsoftware.org/isdl.php)**

3. **Run the build script:**
   ```bash
   # Windows (Command Prompt)
   build.bat
   
   # Or PowerShell
   .\build.ps1
   ```

   This automatically:
   - Builds the Python executable with PyInstaller
   - Packages it with all dependencies
   - Creates the professional Windows installer

4. **Output:** `dist/ResumeAI-Setup-1.0.exe`

For detailed build instructions, see [BUILDING.md](BUILDING.md).

---

## Roadmap

- [x] Flutter desktop GUI with professional styling (v0.3)
- [x] Resume grading with feedback scores (v0.3)
- [ ] File upload with drag-and-drop
- [ ] Cover letter generator
- [ ] LinkedIn summary generator
- [ ] Export to multiple formats (DOCX, HTML)
- [ ] Optional cloud LLM support (Claude / GPT-4) for higher quality
- [ ] macOS and Linux support
- [ ] Professional installer package (.exe, .dmg, .deb)

---

## Author

Built by Robert Asumeng
[LinkedIn](https://www.linkedin.com/in/robertasumeng) | [GitHub](https://github.com/rasumeng)
