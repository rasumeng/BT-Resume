# BT Resume

A free, local AI resume helper that polishes your resume bullets, tailors your resume to job descriptions, and formats new experience — all running privately on your own machine. No API keys, no subscriptions, no data leaving your device.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/rasumeng/BT-Resume)](https://github.com/rasumeng/BT-Resume/releases)

---

## Why BT Resume?

Most AI resume tools cost money, require an account, or send your personal data to external servers. This is my take on a free alternative — built from scratch in Python + React, powered by open-source LLMs that run entirely on your device.

---

## Features

- **Bullet Polish** — rewrites weak resume bullets into strong, ATS-optimized ones using proven resume writing formulas
- **Job Tailoring** — aligns your resume language and keywords to match a specific job description without changing your real experience
- **Experience Updater** — describe a new project or role in plain English and get polished, formatted resume bullets back
- **Resume Grading** — get scores and feedback on your resume's effectiveness
- **PDF + TXT input** — works with both plain text and real PDF resumes
- **PDF output** — generates a clean, formatted PDF resume ready to send
- **Auto-updates** — automatically stays up-to-date with new features and fixes
- **100% offline** — no internet connection required after setup, no API keys, completely free

---

## Tech Stack

| Layer | Tool |
|---|---|---|
| Frontend | React 19 + TypeScript + Vite |
| Backend Language | Python 3.10+ |
| LLM Runtime | [Ollama](https://ollama.com) |
| Bullet Polish Model | Mistral 7B (fast, efficient) |
| PDF Reading | pdfplumber |
| PDF Generation | ReportLab |
| REST API | Flask with CORS |
| Distribution | PyPI (`pip install btr-resume`) |

---

## Quick Start

### Quick Install (pip)

```bash
pip install btr-resume
btr serve
```

Opens the web UI at `http://localhost:5000`.

### Manual Setup (Development)

```bash
# Install Python package in editable mode
pip install -e .

# Build the web frontend
cd web
npm install
npm run build
cd ..

# Start the server
btr serve
```

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) (auto-installed via `btr setup`)
- 8GB+ RAM recommended
- 2GB+ free disk space

---

## Usage

### Application Tabs

| Tab | Description |
|-----|-------------|
| **My Resumes** | View and manage all your resumes |
| **Polish** | Enhance your bullet points with AI |
| **Tailor** | Customize resume for specific job descriptions |
| **Feedback** | Submit feature requests and bug reports |

### First Run Setup

```bash
btr setup
```

This will install Ollama (if needed) and download the AI model (~500MB-1GB).

Then start the app:

```bash
btr serve
```

---

## Project Structure

```
BT-Resume/
├── btr/                          # CLI package (btr serve, btr setup)
│   ├── __init__.py
│   ├── __main__.py               # python -m btr
│   └── cli.py                    # CLI commands
├── backend/                      # Flask REST API
│   ├── app.py                    # Flask app with CORS
│   ├── routes/                   # API endpoint definitions
│   ├── services/                 # Business logic (LLM, PDF, tailoring)
│   └── config.py                 # Backend configuration
├── core/                         # Shared Python modules
│   ├── prompts/                  # LLM prompt templates
│   ├── pdf/                      # PDF generation components
│   ├── resume_model.py           # Data models
│   └── utils.py                  # Utility functions
├── web/                          # React SPA frontend
│   ├── src/                      # Components, screens, styles
│   ├── package.json
│   └── vite.config.ts
├── pyproject.toml
└── README.md
```

---

## Architecture

### Application Flow
```
┌─────────────────────┐
│  React Web UI       │  ← Served by Flask / opened in browser
│  (User Interface)    │
└──────────┬──────────┘
           │ HTTP/JSON (localhost)
           ▼
┌─────────────────────┐
│  Flask REST API     │  ← Python Backend
│  (localhost:5000)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ollama LLM         │  ← Local AI Model (Mistral 7B)
│  (localhost:11434)   │     Runs entirely offline
└─────────────────────┘
```

### API Endpoints
- `GET  /api/health` — Backend health check
- `GET  /api/status` — Detailed service status
- `GET  /api/list-resumes` — List all resumes
- `GET  /api/get-resume` — Load specific resume
- `PUT  /api/update-resume` — Update resume content
- `POST /api/delete-resume` — Delete a resume
- `POST /api/polish-bullets` — Enhance bullet points
- `POST /api/tailor-resume` — Customize for job
- `POST /api/grade-resume` — Score and analyze
- `POST /api/parse-resume` — Parse uploaded resume
- `POST /api/save-resume-pdf` — Generate PDF output

---

## Building from Source

### Prerequisites
- Python 3.10+
- Node.js 18+ (for web frontend)
- Git

### Build Commands

```bash
# Install the package in editable mode
pip install -e .

# Build the web frontend
cd web
npm install
npm run build
cd ..

# Build the Python wheel
python -m build
```

### Output
Built wheel: `dist/btr_resume-*.whl`

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Author

Built by Robert Asumeng
[LinkedIn](https://www.linkedin.com/in/robertasumeng) | [GitHub](https://github.com/rasumeng)