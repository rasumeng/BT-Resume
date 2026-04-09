import pdfplumber
import re
import json
from .llm_client import ask_llm
from .prompts import parse_resume_structure_prompt


HEADER_ALIASES = {
    "WORK EXPERIENCE": {
        "work experience",
        "experience",
        "professional experience",
        "employment",
        "employment history",
        "career history",
    },
    "PROJECTS": {
        "projects",
        "project experience",
        "academic projects",
        "personal projects",
    },
    "LEADERSHIP": {
        "leadership",
        "leadership experience",
        "leadership and activities",
        "campus leadership involvement",
        "activities",
        "involvement",
        "extracurriculars",
    },
    "EDUCATION": {"education", "academic background"},
    "SKILLS": {
        "skills",
        "technical skills",
        "technical / soft skills",
        "technical/soft skills",
        "technicall/soft skills",
        "soft skills",
        "core skills",
        "competencies",
    },
    "SUMMARY": {"summary", "professional summary", "profile"},
}


def _all_header_aliases():
    aliases = []
    for canonical, values in HEADER_ALIASES.items():
        for alias in values:
            aliases.append((alias, canonical))
    # Longer aliases first to avoid partial matches.
    aliases.sort(key=lambda x: len(x[0]), reverse=True)
    return aliases

def load_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()
    # Strip UTF-8 BOM if present
    if text.startswith('\ufeff'):
        text = text[1:]
    return text

def load_pdf(filepath: str) -> str:
    raw_lines = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            raw_lines.extend(text.split("\n"))
    
    # Process and rejoin only lines that are clearly split mid-word
    joined = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].rstrip()  # Remove trailing whitespace
        stripped = line.strip()
        
        if not stripped:
            joined.append("")
            i += 1
            continue
        
        # Only join if current line ends incomplete (mid-word) and next line is a continuation
        while i + 1 < len(raw_lines):
            next_line = raw_lines[i + 1].rstrip().strip()
            
            if not next_line:
                i += 1
                break
            
            words = stripped.split()
            if not words:
                break
                
            last_word = words[-1]
            
            # Check if last word looks truncated at character position
            # Look for common incomplete word endings
            looks_truncated = (
                len(last_word) < 8 and not last_word.endswith(('tion', 'ing', 'ed'))
            ) or last_word.endswith(('d', 'e', 'u', 'a'))  # Cut off at vowel
            
            next_starts_lower = next_line and next_line[0].islower()
            next_is_bullet = next_line and next_line[0] in '●-*'
            
            # Only join if it looks like a sentence fragment continuation
            if looks_truncated and not next_is_bullet and next_starts_lower:
                stripped = stripped + " " + next_line
                i += 1
            else:
                break
        
        joined.append(stripped)
        i += 1
    
    return "\n".join(joined)


def parse_resume_with_mistral(filepath: str) -> dict:
    """
    Unified parser: handles both PDF and TXT files.
    Uses Mistral to extract and structure resume data into JSON.
    
    Args:
        filepath: Path to resume file (PDF or TXT)
    
    Returns:
        dict: Structured resume data with sections like work_experience, projects, leadership, etc.
              Returns None and prints error if parsing fails.
    
    Example return structure:
    {
        "work_experience": [
            {
                "position": "Senior Engineer",
                "company": "Google",
                "location": "Mountain View, CA",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "bullets": [
                    {"text": "Led team...", "has_location": false, "has_date": false}
                ]
            }
        ],
        "projects": [...],
        "leadership": [...],
        "education": [...],
        "skills": [...]
    }
    """
    # Determine file type and extract text
    if filepath.lower().endswith('.pdf'):
        resume_text = load_pdf(filepath)
    elif filepath.lower().endswith(('.txt', '.text')):
        resume_text = load_text(filepath)
    else:
        print(f"ERROR: Unsupported file type. Use .pdf or .txt")
        return None
    
    if not resume_text or not resume_text.strip():
        print(f"ERROR: Could not extract text from {filepath}")
        return None
    
    # Generate parsing prompt
    prompt = parse_resume_structure_prompt(resume_text)
    
    # Call Mistral for structured parsing
    response = ask_llm(prompt, model=None, max_tokens=8192, task_type="parse")
    
    if response is None:
        print("ERROR: Failed to get response from Mistral")
        return None
    
    # Extract and parse JSON from response
    try:
        # Handle markdown code blocks if present
        clean_response = response
        if "```json" in clean_response:
            clean_response = clean_response.replace("```json", "").replace("```", "")
        elif "```" in clean_response:
            clean_response = clean_response.replace("```", "")
        
        # Find JSON object boundaries
        start_idx = clean_response.find('{')
        end_idx = clean_response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            print("ERROR: No JSON found in Mistral response")
            return None
        
        json_str = clean_response[start_idx:end_idx]
        parsed_resume = json.loads(json_str)
        
        return parsed_resume
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON from Mistral response: {e}")
        return None


def _normalize_header_text(line: str) -> str:
    cleaned = line.strip().rstrip(":")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.lower()


def _canonical_header(line: str):
    normalized = _normalize_header_text(line)
    for canonical, aliases in HEADER_ALIASES.items():
        if normalized in aliases:
            return canonical

    # Lightweight keyword fallback for common variants.
    if "experience" in normalized and "project" not in normalized:
        return "WORK EXPERIENCE"
    if "project" in normalized:
        return "PROJECTS"
    if any(token in normalized for token in ["leadership", "activities", "involvement"]):
        return "LEADERSHIP"
    if "education" in normalized:
        return "EDUCATION"
    if "skill" in normalized:
        return "SKILLS"
    return None


def _looks_like_header(line: str, prev_blank: bool, next_blank: bool) -> bool:
    stripped = line.strip().rstrip(":")
    if not stripped:
        return False
    if stripped.startswith(("-", "*", "●")):
        return False
    if any(ch.isdigit() for ch in stripped):
        return False
    
    # Increased length limit to allow for longer project titles
    # (e.g., "Housing Price Prediction — End-to-End ML Pipeline | Python, Pandas, Scikit-learn")
    if len(stripped) > 100:
        return False

    # Avoid classifying the candidate's name as a section header.
    if _looks_like_name(stripped):
        return False

    words = stripped.split()
    if not (1 <= len(words) <= 10):  # Increased word count limit
        return False

    is_title_case = all((w[:1].isupper() or w.isupper()) for w in words)
    if not (stripped.isupper() or is_title_case):
        return False

    # Resume headers are usually visually separated.
    return prev_blank or next_blank


def _looks_like_name(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if "@" in stripped or "http" in stripped.lower() or "www." in stripped.lower():
        return False
    if any(ch.isdigit() for ch in stripped):
        return False
    words = [w for w in stripped.split() if w]
    if not (2 <= len(words) <= 5):
        return False
    # Allow uppercase or title-case names, avoid punctuation-heavy lines.
    if any(ch in stripped for ch in "|/:;"):
        return False
    return all(any(c.isalpha() for c in w) for w in words)


def _split_inline_header(line: str):
    for alias, canonical in _all_header_aliases():
        escaped_alias = re.escape(alias)
        pattern = rf"^\s*{escaped_alias}\s*[:\-—]\s*(.+?)\s*$"
        match = re.match(pattern, line, flags=re.IGNORECASE)
        if match:
            remainder = match.group(1).strip()
            return canonical, remainder
    return None, None

def _extract_contact_info(header_text: str) -> dict:
    """Extract email, phone, LinkedIn, and GitHub from header text."""
    contact = {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
    }
    
    # Extract email (look for @)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", header_text)
    if email_match:
        contact["email"] = email_match.group(0)
    
    # Extract phone (common formats)
    phone_match = re.search(r"(?:\+\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})", header_text)
    if phone_match:
        contact["phone"] = phone_match.group(0).strip()
    
    # Extract LinkedIn URL - with or without protocol
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-\.]+/?", header_text, re.IGNORECASE)
    if linkedin_match:
        url = linkedin_match.group(0).rstrip('/')
        # Add protocol if missing
        if not url.startswith("http"):
            url = "https://" + url
        contact["linkedin"] = url
    
    # Extract GitHub URL - with or without protocol
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w\-\.]+/?", header_text, re.IGNORECASE)
    if github_match:
        url = github_match.group(0).rstrip('/')
        # Add protocol if missing
        if not url.startswith("http"):
            url = "https://" + url
        contact["github"] = url
    
    return contact


def parse_section(text: str) -> dict:
    sections = {}
    current_section = None
    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        prev_blank = i == 0 or not lines[i - 1].strip()
        next_blank = i == len(lines) - 1 or not lines[i + 1].strip()

        inline_canonical, inline_remainder = _split_inline_header(stripped)
        if inline_canonical:
            current_section = inline_canonical
            sections.setdefault(current_section, "")
            if inline_remainder:
                sections[current_section] += inline_remainder + "\n"
            continue

        canonical = _canonical_header(stripped)
        if canonical or _looks_like_header(stripped, prev_blank, next_blank):
            current_section = canonical or stripped.rstrip(":").upper()
            sections.setdefault(current_section, "")
            continue

        if current_section is None:
            current_section = "_HEADER"
            sections.setdefault(current_section, "")
        sections[current_section] += stripped + "\n"
    
    # Extract and store contact info separately
    header_text = sections.get("_HEADER", "")
    contact_info = _extract_contact_info(header_text)
    sections["_CONTACT"] = contact_info
    
    return sections

def parse_subsections(section_text: str, section_name: str = "") -> list:
    subsections = []
    current = None
    lines = section_text.split("\n")
    
    # Only apply aggressive continuation merging for PROJECTS section
    is_projects = section_name == "PROJECTS"

    # Known section headers — stop accumulating if we hit one
    KNOWN_HEADERS = {
        "WORK EXPERIENCE", "EXPERIENCE", "PROJECTS", "LEADERSHIP", "EDUCATION",
        "SKILLS", "TECHNICAL SKILLS", "SUMMARY", "CERTIFICATIONS", "VOLUNTEERING",
    }

    def looks_like_location_or_company(line: str) -> bool:
        """Check if line looks like a company/location line rather than a job title."""
        # Company locations typically:
        # - End with a city, state, or "Remote"
        # - Contain a company name (capitalized)
        # - Are SHORT (2-4 words) with few action words
        # - Examples: "Best Buy Cedar Hill, TX", "FAPEMPA LLC Remote", "Microsoft Seattle, WA"
        words = line.split()
        if len(words) <= 4:  # Company/location lines are typically short
            # Check if it ends with a US state or location indicator
            state_abbrevs = {"TX", "CA", "NY", "FL", "WA", "MA", "IL", "PA", "VA", "NC", "GA", "OH", "MI"}
            if any(word in state_abbrevs for word in words) or line.endswith("Remote"):
                return True
            # Check if it looks like pure company + location (no verbs, few words)
            if len(words) <= 3 and "," in line:  
                return True
        return False

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            # empty line - skip it
            pass
        # Stop if we've hit what looks like the start of a new section
        elif line.upper().rstrip(":") in KNOWN_HEADERS:
            break
        # Bullet Branch
        elif line.startswith("*") or line.startswith("-") or line.startswith("●") or line.startswith("•"):
            if current is not None:
                clean = line.lstrip("*-●•· ").strip()
                if clean:
                    current["bullets"].append(clean)
    
        # Title or continuation
        else:
            # Check if this looks like a title:
            # - Starts with capital letter AND
            # - Either has a colon, dash, or is 2-7 words AND
            # - Doesn't look like a sentence fragment (doesn't end with lowercase continuation)
            looks_like_title = (
                line and 
                line[0].isupper() and 
                ((':' in line or '—' in line or '–' in line or '|' in line) or (2 <= len(line.split()) <= 7)) and
                not (line.startswith('and ') or line.startswith('or ') or line.lower().startswith(('achieving', 'driving', 'improving', 'increasing', 'creating', 'building')))
            )
            
            # Check if this is likely a company/location continuation
            is_company_location = looks_like_location_or_company(line)
            
            # If we have a current subsection and current line is not a new title,
            # add it as part of the title or as a bullet
            if current is not None and (not looks_like_title or is_company_location):
                # This is either a continuation of the title (company/location) or a non-bullet line
                if current["bullets"]:
                    # We already have bullets, so append to last bullet
                    current["bullets"][-1] += " " + line
                else:
                    # No bullets yet, so append to title (this is company/location info)
                    current["title"] += " " + line
            elif is_projects and current is not None and looks_like_title and len(line.split()) <= 3 and current["bullets"]:
                # For PROJECTS: If this "title" is very short (2-3 words),
                # it's likely a continuation of the last bullet (from line wrapping in PDF)
                current["bullets"][-1] += " " + line
            else:
                # This is a new title
                if current is not None:
                    subsections.append(current)
                current = {"title": line, "bullets": []}
    
    # save the last subsection
    if current is not None:
        subsections.append(current)
    
    return subsections


if __name__ == "__main__":
    text = load_pdf("samples/resume.pdf")
    sections = parse_section(text)
    
    print("=== CONTACT INFORMATION ===")
    contact = sections.get("_CONTACT", {})
    print(f"Email: {contact.get('email')}")
    print(f"Phone: {contact.get('phone')}")
    print(f"LinkedIn: {contact.get('linkedin')}")
    print(f"GitHub: {contact.get('github')}")
    print()

    print("=== WORK EXPERIENCE SECTION ===")
    if "WORK EXPERIENCE" in sections:
        subsections = parse_subsections(sections["WORK EXPERIENCE"], "WORK EXPERIENCE")
        for i, sub in enumerate(subsections):
            print(f"\n{i+1}. TITLE: {sub['title']}")
            for j, b in enumerate(sub['bullets']):
                print(f"   • {b[:100]}{'...' if len(b) > 100 else ''}")

    print("=== PROJECTS SECTION ===")
    if "PROJECTS" in sections:
        subsections = parse_subsections(sections["PROJECTS"], "PROJECTS")
        for i, sub in enumerate(subsections):
            print(f"\n{i+1}. TITLE: {sub['title']}")
            for j, b in enumerate(sub['bullets']):
                print(f"   • {b[:100]}{'...' if len(b) > 100 else ''}")
    
    else:
        print("No PROJECTS section found")
    print()