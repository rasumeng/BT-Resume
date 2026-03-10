import pdfplumber

def load_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()
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

def parse_section(text: str) -> dict:
    sections = {}
    current_section = None
    lines = text.split("\n")
    for line in lines:
        if line.strip().isupper():
            current_section = line.strip()
            sections[current_section] = ""
        else:
            if current_section is None:
                continue
            sections[current_section] += line.strip() + "\n"
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
    subsections = parse_subsections(sections["WORK EXPERIENCE"])
    for sub in subsections:
        print("TITLE:", sub["title"])
        for b in sub["bullets"]:
            print("  BULLET:", b)
        print()