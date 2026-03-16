import pdfplumber
import re


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
    
    # Rejoin wrapped lines
    joined = []
    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            joined.append("")
            continue
        # If line doesn't start with a bullet or look like a header
        # anad previous line exists, it's a continuation
        if (joined and
            not stripped.startswith("●") and 
            not stripped.startswith("-") and
            not stripped.startswith("*") and
            not stripped.isupper() and
            stripped[0].islower()):
            joined[-1] = joined[-1] + " " + stripped
        else:
            joined.append(stripped)
    return "\n".join(joined)


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
    if len(stripped) > 45:
        return False

    # Avoid classifying the candidate's name as a section header.
    if _looks_like_name(stripped):
        return False

    words = stripped.split()
    if not (1 <= len(words) <= 5):
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
    return sections

def parse_subsections(section_text: str) -> list:
    subsections = []
    current = None
    lines = section_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            #empty line - skip it
            pass
        # Bullet Branch
        elif line.startswith("*") or line.startswith("-") or line.startswith("●"):
            if current is not None:
                clean = line.lstrip("*-● ").strip()
                current["bullets"].append(clean)
    
        # Title
        else:
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
    if "WORK EXPERIENCE" in sections:
        subsections = parse_subsections(sections["WORK EXPERIENCE"])
        for sub in subsections:
            print("TITLE:", sub["title"])
            for b in sub["bullets"]:
                print("  BULLET:", b)
            print()