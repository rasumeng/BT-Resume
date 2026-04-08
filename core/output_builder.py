import os
import re

from core.input_parser import load_pdf, parse_section, parse_subsections
from core.prompts import bullet_polish_prompt, job_tailor_prompt
from core.llm_client import ask_llm

SECTIONS_TO_POLISH = ["WORK EXPERIENCE", "PROJECTS", "LEADERSHIP", "SKILLS"]


def build_resume(sections: dict, job_description) -> dict:
    improved_sections = {}
    for section, content in sections.items():
        # Skip non-string values like dicts (e.g., _CONTACT)
        if not isinstance(content, str):
            improved_sections[section] = content
            continue
        if section in SECTIONS_TO_POLISH:
            improved_sections[section] = polish_section(content, job_description, section)
        else:
            improved_sections[section] = content
    return improved_sections    

def polish_section(section_text: str, job_description, section_name: str = "") -> str:
    subsections = parse_subsections(section_text, section_name)
    polish_mode = os.getenv("BULLET_POLISH_MODE", "medium").lower()
    result = ""
    
    for idx, sub in enumerate(subsections):
        titles = sub["title"]
        bullets = sub["bullets"]
        if not bullets:
            result += titles + "\n\n"
            continue

        if job_description:
            # For job tailoring, keep subsection context and bullet count.
            bullets_text = "\n".join(bullets)
            prompt = job_tailor_prompt(bullets_text, job_description)
            polished = ask_llm(prompt)
            polished = clean_bullets(polished)
            if not polished:
                polished = "\n".join(f"- {b}" for b in bullets)
        else:
            # Bullet polish prompt expects one bullet, so process per bullet.
            polished_lines = []
            for bullet in bullets:
                prompt = bullet_polish_prompt(bullet, mode=polish_mode)
                polished_one = ask_llm(prompt)
                cleaned_one = clean_bullets(polished_one)
                if cleaned_one:
                    # Take only the first bullet line — never accept merged multi-sentence output
                    first_line = cleaned_one.split("\n")[0].strip()
                    # Sanity check: if the model returned something way too long it likely
                    # merged bullets. Fall back to the original in that case.
                    if len(first_line) <= 300:
                        polished_lines.append(first_line)
                    else:
                        polished_lines.append(f"- {bullet}")
                else:
                    polished_lines.append(f"- {bullet}")
            polished = "\n".join(polished_lines)

        result += titles + "\n"
        result += polished + "\n"
        result += "\n"

    return result.strip()
                    

def clean_bullets(text: str) -> str:
    if not text:
        return ""
    lines = text.strip().split("\n")
    cleaned = []
    skip_phrases = ["note:", "here is", "i've", "i have", "rewritten", "the above", "(note"]
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip commentary lines first
        if any(line.lower().startswith(phrase) for phrase in skip_phrases):
            continue
        # Strip bracket-only artifact lines like "[N/A for measurable result]"
        if re.match(r"^\[.*\]$", line):
            continue
        # Remove leading numbers like "1." "2." etc
        if line[0].isdigit() and len(line) > 1 and line[1] in ".):":
            line = "- " + line[2:].strip()
        # Normalize bullet prefix: strip any combo of -, *, •, ● then re-add "- "
        line = re.sub(r"^[-*•●·]+\s*", "", line).strip()
        if line:
            cleaned.append(f"- {line}")
    return "\n".join(cleaned)


def append_experience_entry(filepath, section, title, bullets, output_path=None):
    from core.pdf_generator import generate_pdf

    text = load_pdf(filepath)
    sections = parse_section(text)
    if not sections:
        raise ValueError("Could not parse resume sections from selected PDF.")

    cleaned_section = (section or "").strip().upper()
    cleaned_title = (title or "").strip()
    cleaned_bullets = [b.strip().lstrip("-* ") for b in (bullets or []) if b and b.strip()]

    if not cleaned_section:
        raise ValueError("Section is required.")
    if not cleaned_title:
        raise ValueError("Experience title is required.")
    if not cleaned_bullets:
        raise ValueError("At least one bullet is required.")

    entry_lines = [cleaned_title]
    entry_lines.extend([f"- {bullet}" for bullet in cleaned_bullets])
    entry_text = "\n".join(entry_lines).strip()

    existing = sections.get(cleaned_section, "").rstrip()
    if existing:
        sections[cleaned_section] = f"{existing}\n\n{entry_text}\n"
    else:
        sections[cleaned_section] = f"{entry_text}\n"

    destination = output_path or filepath
    generate_pdf(sections, destination)
    return destination

if __name__ == "__main__":
    from core.input_parser import load_text
    
    text = load_text("samples/resume.txt")
    sections = parse_section(text)
    improved = build_resume(sections, None)

    # improved = build_resume(sections)
    for header, content in improved.items():
        print(f"--- {header} ---")
        print(content)
        print()