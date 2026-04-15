# Flask API Documentation

## Overview

The Resume AI backend is a Flask-based REST API that provides all resume processing functionality. The Flutter desktop app communicates with this API via HTTP.

## Architecture

```
Flutter Desktop App
   ↓ HTTP (JSON)
Flask API (http://localhost:5000/api)
   ↓
Core Python Services
   ├── File Service (resume I/O)
   ├── LLM Service (AI processing)
   └── PDF Generation
   ↓
Ollama (LLM Runtime)
```

## Base URL

```
http://localhost:5000/api
```

## Response Schema

All endpoints return JSON in this format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "error": "Error message description",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## Endpoints

### File Operations

#### 1. Health Check
**Endpoint:** `GET /health`

**Purpose:** Verify backend is running (Flutter uses this on startup)

**Response:**
```json
{
  "status": "healthy",
  "service": "resume-ai-api",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

#### 2. List Resumes
**Endpoint:** `GET /list-resumes`

**Purpose:** Get all resumes in the resumes folder

**Query Parameters:** None

**Response:**
```json
{
  "success": true,
  "resumes": [
    {
      "name": "Roberts_Resume.txt",
      "path": "/absolute/path/to/Robert_Resume.txt",
      "size": 1024,
      "modified": 1776184752.4378002,
      "created": 1775767052.749728
    }
  ]
}
```

---

#### 3. Get Resume Content
**Endpoint:** `GET /get-resume`

**Purpose:** Load a resume file's content

**Query Parameters:**
- `filename` (required): Name of the resume file

**Example:**
```
GET /get-resume?filename=Roberts_Resume.txt
```

**Response:**
```json
{
  "success": true,
  "content": "John Roberts\nEmail: john@email.com\n...",
  "filename": "Roberts_Resume.txt"
}
```

---

#### 4. Save Resume PDF
**Endpoint:** `POST /save-resume-pdf`

**Purpose:** Generate and save a PDF from parsed resume data

**Request Body:**
```json
{
  "filename": "Roberts_Resume.pdf",
  "resume_text": {
    "name": "John Roberts",
    "contact": "john@email.com | 555-1234 | linkedin.com/in/john",
    "education": [...],
    "technical_skills": [...],
    "work_experience": [...],
    "projects": [...],
    "leadership": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "filename": "Roberts_Resume.pdf",
  "path": "/absolute/path/to/Roberts_Resume.pdf"
}
```

---

#### 5. Update Resume
**Endpoint:** `POST /update-resume`

**Purpose:** Update an existing resume file

**Request Body:**
```json
{
  "filename": "Roberts_Resume.txt",
  "content": "Updated resume content..."
}
```

**Response:**
```json
{
  "success": true,
  "filename": "Roberts_Resume.txt"
}
```

---

#### 6. Delete Resume
**Endpoint:** `DELETE /delete-resume`

**Purpose:** Delete a resume and associated metadata

**Query Parameters:**
- `filename` (required): Name of the resume file

**Example:**
```
DELETE /delete-resume?filename=Roberts_Resume.txt
```

**Response:**
```json
{
  "success": true,
  "deleted": "Roberts_Resume.txt"
}
```

---

### LLM Operations (AI Processing)

#### 7. Polish Bullets
**Endpoint:** `POST /polish-bullets`

**Purpose:** Rewrite resume bullets to be stronger and ATS-optimized

**Request Body:**
```json
{
  "bullets": [
    "Managed team of 5 people",
    "Did some work with Python"
  ],
  "intensity": "medium"
}
```

**Parameters:**
- `intensity`: "light" | "medium" | "heavy" (default: "medium")

**Response:**
```json
{
  "success": true,
  "bullets": [
    "Led cross-functional team of 5 engineers, delivering Q3 roadmap 2 weeks ahead of schedule",
    "Designed and implemented Python-based data pipeline processing 1M+ records/day with 99.9% uptime"
  ]
}
```

---

#### 8. Tailor Resume
**Endpoint:** `POST /tailor-resume`

**Purpose:** Reframe resume to match a specific job description

**Request Body:**
```json
{
  "resume_text": "Full resume content here...",
  "job_description": "Full job description here..."
}
```

**Response:**
```json
{
  "success": true,
  "tailored_resume": "Tailored resume content matching job description..."
}
```

---

#### 9. Grade Resume
**Endpoint:** `POST /grade-resume`

**Purpose:** Score and provide feedback on a resume

**Request Body:**
```json
{
  "resume_text": "Full resume content here..."
}
```

**Response:**
```json
{
  "success": true,
  "grade": {
    "score": 78,
    "strengths": [
      "Strong technical background",
      "Good project diversity",
      "Clear formatting"
    ],
    "improvements": [
      "Add more impact metrics",
      "Include more leadership examples",
      "Quantify achievements better"
    ],
    "recommendations": [
      "Add bullet points with percentages/numbers",
      "Include keywords from target roles",
      "Add 2-3 more projects showing progression"
    ]
  }
}
```

---

#### 10. Parse Resume to PDF Format
**Endpoint:** `POST /parse-resume`

**Purpose:** Parse raw resume text into structured JSON format for PDF generation

**Request Body:**
```json
{
  "resume_text": "Full resume content here..."
}
```

**Response:**
```json
{
  "success": true,
  "parsed_resume": {
    "name": "John Roberts",
    "contact": "john@email.com | 555-1234",
    "education": [...],
    "technical_skills": [...],
    "work_experience": [...],
    "projects": [...],
    "leadership": [...]
  }
}
```

---

## Error Handling

### Common Error Responses

**400 - Bad Request**
```json
{
  "success": false,
  "error": "filename and content required"
}
```

**404 - Not Found**
```json
{
  "success": false,
  "error": "Resume not found: missing_file.txt"
}
```

**500 - Server Error**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

## Startup Sequence (for Flutter)

The Flutter app should follow this sequence when launching:

1. **Start Backend Process**
   ```
   Python subprocess: python run_backend.py
   ```

2. **Wait for Health Check** (with timeout)
   ```
   GET /api/health
   Retry every 500ms until success (max 30 seconds)
   ```

3. **Load Initial Data**
   ```
   GET /api/list-resumes
   ```

4. **Display UI**
   - Show resume list from step 3
   - User can interact with app

---

## Development

### Starting the Backend

```bash
# From project root
cd BTF-Resume
.\venv\Scripts\python.exe run_backend.py
```

### Testing Endpoints

Using curl (PowerShell):
```powershell
# Health check
curl.exe -s http://localhost:5000/api/health

# List resumes
curl.exe -s http://localhost:5000/api/list-resumes

# Get resume content
curl.exe -s "http://localhost:5000/api/get-resume?filename=Roberts_Resume.txt"
```

---

## Configuration

Backend configuration is in `backend/config.py`:

```python
FLASK_HOST = "127.0.0.1"      # localhost only (secure)
FLASK_PORT = 5000              # Port number
OLLAMA_HOST = "http://localhost:11434"  # Ollama location
```

**Important:** Backend only listens on localhost (`127.0.0.1`). This is secure - no external network access.

---

## Future Enhancements

- [ ] WebSocket support for real-time processing updates
- [ ] Batch processing endpoints
- [ ] Authentication for multi-user support
- [ ] Cloud storage integration (AWS S3, Azure Blob)
- [ ] Export to multiple formats (DOCX, Google Docs)
