# BT Resume

A free, local AI resume helper that polishes your resume bullets, tailors your resume to job descriptions, and formats new experience — all running privately on your own machine. No API keys, no subscriptions, no data leaving your device.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/btr-resume)](https://pypi.org/project/btr-resume/)
[![Python Versions](https://img.shields.io/pypi/pyversions/btr-resume)](https://pypi.org/project/btr-resume/)
[![GitHub Release](https://img.shields.io/github/v/release/rasumeng/BT-Resume)](https://github.com/rasumeng/BT-Resume/releases)

---

## Quick Start

### Prerequisites
- **Python 3.10+** — [Download Python](https://python.org/downloads)
- **Ollama** — Download from [ollama.com](https://ollama.com) (handled automatically on first run)

### Install & Run

```bash
pip install btr-resume
btr serve
```

That's it. Your browser opens to `http://localhost:5000` with the BT Resume web UI.

> **First run:** `btr serve` will automatically attempt to start Ollama and download the Mistral 7B model (~4.1GB). If Ollama is not installed, you'll be prompted to install it from [ollama.com](https://ollama.com).

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
- **100% offline** — no internet connection required after setup, no API keys, completely free

---

## Commands

| Command | Description |
|---------|-------------|
| `btr serve` | Start the server and open the browser (same as plain `btr`) |
| `btr` | Start the server and open the browser |
| `btr setup` | Manual setup: install Ollama and download the AI model |

---

## Configuration

BT Resume is zero-config by default, but you can customize via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `BT_RESUME_HOST` | `127.0.0.1` | Server bind address |
| `BT_RESUME_PORT` | `5000` | Server port |
| `BT_RESUME_DEBUG` | `false` | Enable debug logging |
| `BT_RESUME_OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama server URL |
| `BT_RESUME_ENABLE_ANALYTICS` | `true` | Anonymous usage tracking (set to `false` to disable) |
| `BT_RESUME_SECRET_KEY` | *(auto-generated)* | Flask secret key (persisted across restarts) |

Example:

```bash
BT_RESUME_PORT=8080 BT_RESUME_DEBUG=true btr serve
```

---

## Requirements

- **OS:** Windows, macOS, or Linux
- **Python:** 3.10+
- **RAM:** 8GB+ recommended
- **Disk:** 2GB+ free space (for the AI model)
- **Ollama:** Installed automatically on first run

---

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | React 19 + TypeScript + Vite |
| Backend | Python 3.10+ / Flask |
| LLM Runtime | [Ollama](https://ollama.com) |
| AI Model | Mistral 7B (fast, efficient) |
| PDF Reading | pdfplumber |
| PDF Generation | ReportLab |
| Distribution | PyPI — `pip install btr-resume` |

---

## Building from Source

```bash
# Clone the repo
git clone https://github.com/rasumeng/BT-Resume.git
cd BT-Resume

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

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Author

Built by Robert Asumeng
[LinkedIn](https://www.linkedin.com/in/robertasumeng) | [GitHub](https://github.com/rasumeng)
