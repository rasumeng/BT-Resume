# BTF-Resume LLM Pipeline - Complete Flow

## Overview
The BTF-Resume project uses Ollama (local LLM service) to process resume content through multiple specialized prompts. Below is the exact pipeline for each feature.

---

## 1. BULLET POLISH PIPELINE

### Flow Diagram
```
User clicks "Polish Resume"
    ↓
Load PDF from file
    ↓
Parse resume into sections (WORK EXPERIENCE, PROJECTS, LEADERSHIP, SKILLS, etc.)
    ↓
For each section marked for polishing:
    ↓
    Parse subsections (e.g., "Software Engineer @ Company" with its bullets)
    ↓
    FOR EACH BULLET individually:
        ├─ Create bullet_polish_prompt(bullet, mode="medium|light|aggressive")
        ├─ Send to LLM (ask_llm(prompt))  <-- FIRST LLM CALL (PER BULLET)
        ├─ Receive polished bullet from model
        ├─ Clean response (remove numbering, ensure "- " prefix)
        └─ Store polished bullet
    ↓
Combine all polished bullets back into document
    ↓
Create changes_summary_prompt(original, polished)
    ↓
Send to LLM (ask_llm(prompt))  <-- SECOND LLM CALL (ONCE FOR ENTIRE RESUME)
    ↓
Parse JSON response with up to 8 change descriptions
    ↓
Display to user
```

### Key Code Path
1. **BulletPolishPanel.polish_resume()** → starts thread
2. **BulletPolishPanel._run_polish(path)** → orchestrates flow
   - `load_pdf(path)` → read PDF
   - `parse_section(text)` → extract sections
   - `build_resume(sections, job_description=None)` → call polishing
3. **output_builder.build_resume()** → loop sections
4. **output_builder.polish_section(section_text, job_description=None, section_name)** → core logic
   - `parse_subsections()` → get experience entries
   - **For each bullet:**
     - `ask_llm(bullet_polish_prompt(bullet))` ← LLM CALL #N
5. Back in **_run_polish():**
   - `ask_llm(get_changes_summary_prompt(...))` ← LLM CALL #(N+1)

### LLM Calls Made
- **Per bullet:** 1 call (YES, you were right - one per bullet)
- **After all bullets:** 1 additional call for changes summary
- **Total calls:** Number of bullets + 1

### Example
Resume has 3 bullets → 3 LLM calls for polishing + 1 for summary = **4 total calls**

---

## 2. JOB TAILOR PIPELINE

### Flow Diagram
```
User selects resume + uploads job description
    ↓
Load PDF, parse sections
    ↓
For each section marked for polishing:
    ↓
    Parse subsections
    ↓
    FOR EACH SUBSECTION (NOT individual bullets):
        ├─ Combine all bullets in subsection into text
        ├─ Create job_tailor_prompt(bullets_text, job_description)
        ├─ Send to LLM (ask_llm(prompt))  <-- LLM CALL
        ├─ Receive tailored bullets (multiple lines)
        ├─ Clean response
        └─ Store polished bullets
    ↓
Combine all tailored bullets back into document
    ↓
Create changes_summary_prompt (same as bullet polish)
    ↓
Send to LLM (ask_llm(prompt))  <-- SECOND LLM CALL
    ↓
Display to user
```

### Key Difference from Bullet Polish
- **Bullet Polish:** 1 LLM call PER BULLET
- **Job Tailor:** 1 LLM call PER SUBSECTION (all bullets at once)

### Example
- Experience section with 3 jobs × 4 bullets each (12 total bullets)
- Bullet Polish: 12 calls + 1 summary = 13 calls
- Job Tailor: 3 calls (one per job) + 1 summary = 4 calls

---

## 3. EXPERIENCE UPDATER PIPELINE

### Flow Diagram
```
User describes experience in text field
    ↓
Create experience_updater_prompt(user_input)
    ↓
Send to LLM (ask_llm(prompt))  <-- LLM CALL
    ↓
Receive 2-4 formatted bullets
    ↓
Parse and format bullets
    ↓
Return to user
```

### LLM Calls
- **1 call** to generate bullets from description

---

## 4. RESUME GRADER PIPELINE

### Flow Diagram
```
User clicks "Grade Resume"
    ↓
Parse resume sections
    ↓
Create get_grader_prompt(resume_text)
    ↓
Send to LLM (ask_llm(prompt))  <-- LLM CALL
    ↓
Receive JSON: {"ats_score": X, "sections_score": X, "bullets_score": X, "keywords_score": X}
    ↓
Parse and display scores as progress bars
```

### LLM Calls
- **1 call** to grade entire resume

---

## LLM CONNECTION DETAILS

### Technology Stack
- **Service:** Ollama (local LLM inference)
- **Endpoint:** `http://localhost:11434/api/generate`
- **Default Model:** `mistral:7b` (or OLLAMA_MODEL env var)

### Request Structure
```python
POST http://localhost:11434/api/generate

{
  "model": "mistral:7b",
  "prompt": "<prompt text>",
  "stream": False,
  "options": {
    "num_predict": 1024,
    "temperature": 0.4
  }
}
```

### Response Structure
```python
{
  "response": "<generated text>",
  ...
}
```

### Timeout
- **120 seconds** per LLM call

---

## PROMPT TEMPLATES

### 1. bullet_polish_prompt(bullet, mode="medium")
**Inputs:**
- `bullet` (str): Single resume bullet
- `mode` (str): "light", "medium", or "aggressive"

**Output:** Single polished bullet (without "- " prefix)

**Key Instructions to Model:**
- Max 180 characters
- Action Verb + Task + Tools + Impact
- Preserve all technologies
- Use strong verbs (Engineered, Built, Automated, Optimized...)
- Add metrics if needed (with placeholders [X%], [N users])
- Do NOT invent experience

---

### 2. job_tailor_prompt(resume_section, job_description)
**Inputs:**
- `resume_section` (str): Multiple bullets from one subsection
- `job_description` (str): Full job description text

**Output:** Multiple tailored bullets (without "- " prefix)

**Key Instructions to Model:**
- Same number of bullets as input
- Mirror keywords from job description
- Preserve original accomplishments
- Do NOT add skills not in original resume
- Max 180 characters per bullet
- Do NOT copy responsibilities from job posting

---

### 3. get_changes_summary_prompt(original, polished)
**Inputs:**
- `original` (str): Formatted original resume
- `polished` (str): Formatted polished resume

**Output:** JSON array of up to 8 change descriptions

**Format:** `["change 1", "change 2", ...]`

**Model Instructions:**
- Focus on meaningful changes (verb upgrades, keywords, structure)
- Each change under 80 characters
- Ignore whitespace differences

---

### 4. experience_updater_prompt(user_input)
**Inputs:**
- `user_input` (str): Natural language description of experience

**Output:** 2-4 formatted resume bullets (with "- " prefix)

**Key Instructions to Model:**
- Extract distinct accomplishments
- Structure: Action Verb + Task + Tools + Result
- Max 180 characters per bullet
- Add metrics or use placeholders
- Use strong verbs
- No generic phrases

---

### 5. get_grader_prompt(resume_text)
**Inputs:**
- `resume_text` (str): Full resume text

**Output:** JSON object with 4 scores (1-10 each)

**Format:**
```json
{
  "ats_score": 0-10,
  "sections_score": 0-10,
  "bullets_score": 0-10,
  "keywords_score": 0-10
}
```

---

## ENVIRONMENT VARIABLES

```bash
OLLAMA_MODEL=mistral:7b          # Model to use (default)
BULLET_POLISH_MODE=medium        # Rewrite intensity: light, medium, aggressive
```

---

## ERROR HANDLING

### Connection Error
- If Ollama is not running: `"Error connecting to Ollama: ..."`
- Retry logic: None (synchronous call, times out after 120s)

### Empty Response
- If model returns empty: Falls back to original text
- Polish marked as incomplete

### Parse Error
- If JSON parse fails: Falls back to defaults
- Changes summary returns empty list

---

## CALL COUNT BY FEATURE

| Feature | Calls | Factors |
|---------|-------|---------|
| Bullet Polish | N + 1 | N = number of bullets |
| Job Tailor | M + 1 | M = number of subsections |
| Experience Add | 1 | Fixed |
| Resume Grade | 1 | Fixed |
| Changes Summary | +1 | Always added to polish/tailor |

---

## MODEL BEHAVIOR TUNING

### Temperature (currently 0.4)
- **Lower (0.0-0.3):** More deterministic, conservative edits
- **Higher (0.5-1.0):** More creative, varied rewrites
- **Current (0.4):** Balanced between consistency and variety

### Max Tokens (currently 1024)
- Limits response length
- 180 char bullets rarely exceed 256 tokens
- Buffer for thinking/explanation text

### Model Choice
- **mistral:7b:** Fast, good at instruction following, concise
- Alternative: llama2, neural-chat, etc.

---

## OPTIMIZATION OPPORTUNITIES

1. **Batch Processing:** Could send multiple bullets at once instead of per-bullet
2. **Caching:** Cache identical bullets to skip redundant LLM calls
3. **Async:** Already uses threading, could parallelize some calls
4. **Fallback:** Could use multiple models if one fails
5. **Streaming:** Enable streaming responses for faster perceived performance

---

## COMPLETE CALL SEQUENCE EXAMPLE

**Scenario:** User polishes a resume with 2 jobs (3 bullets each) + 2 projects (2 bullets each)

```
1. Load PDF
2. Parse sections
3. Process WORK EXPERIENCE:
   4. Call LLM → Polish job 1, bullet 1
   5. Call LLM → Polish job 1, bullet 2
   6. Call LLM → Polish job 1, bullet 3
   7. Call LLM → Polish job 2, bullet 1
   8. Call LLM → Polish job 2, bullet 2
   9. Call LLM → Polish job 2, bullet 3
10. Process PROJECTS:
   11. Call LLM → Polish project 1, bullet 1
   12. Call LLM → Polish project 1, bullet 2
   13. Call LLM → Polish project 2, bullet 1
   14. Call LLM → Polish project 2, bullet 2
15. Get changes summary:
   16. Call LLM → Generate summary of all changes
17. Display to user

TOTAL: 13 LLM calls
```
