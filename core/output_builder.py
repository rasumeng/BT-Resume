import os
import re
import json

from core.input_parser import load_pdf, parse_section, parse_subsections
from core.prompts import bullet_polish_prompt, job_tailor_prompt
from core.llm_client import ask_llm

# Section names as they appear in structured format from Mistral
STRUCTURED_SECTIONS_TO_POLISH = ["work_experience", "projects", "leadership"]


def build_resume(sections: dict, job_description) -> dict:
    """
    Improve resume by polishing/tailoring sections.
    
    Works with structured JSON format from parse_resume_with_mistral():
    {
        "work_experience": [{"position": "...", "bullets": [...]}],
        "projects": [...],
        "leadership": [...]
    }
    
    Args:
        sections: Structured resume sections dict from Mistral parser
        job_description: Job description for tailoring (optional)
    
    Returns:
        Improved sections dict
    """
    improved_sections = {}
    
    for section_name, entries in sections.items():
        # Skip if not a list (e.g., skills might be string/list or contact info)
        if not isinstance(entries, list):
            improved_sections[section_name] = entries
            continue
        
        # Only polish certain sections
        if section_name not in STRUCTURED_SECTIONS_TO_POLISH:
            improved_sections[section_name] = entries
            continue
        
        # Polish each entry in the section
        improved_entries = []
        for entry in entries:
            if isinstance(entry, dict) and "bullets" in entry:
                improved_entry = polish_entry(entry, job_description, section_name)
                improved_entries.append(improved_entry)
            else:
                improved_entries.append(entry)
        
        improved_sections[section_name] = improved_entries
    
    return improved_sections


def polish_entry(entry: dict, job_description, section_name: str = "") -> dict:
    """
    Polish a single structured entry from Mistral format.
    
    Entry structure:
    {
        "position": "...",
        "company": "...",
        "bullets": [
            {"text": "...", "has_location": false, "has_date": false}
        ]
    }
    """
    polish_mode = os.getenv("BULLET_POLISH_MODE", "medium").lower()
    improved_entry = entry.copy()
    
    if "bullets" not in entry:
        return improved_entry
    
    original_bullets = entry["bullets"]
    if not original_bullets:
        return improved_entry
    
    # Extract bullet texts
    bullet_texts = [b.get("text", "") if isinstance(b, dict) else b for b in original_bullets]
    
    if job_description:
        # For job tailoring, process all bullets together for context
        bullets_text = "\n".join([f"- {b}" for b in bullet_texts])
        prompt = job_tailor_prompt(bullets_text, job_description)
        polished = ask_llm(prompt, task_type="tailor")
        polished = clean_bullets(polished)
        if not polished:
            polished = "\n".join(f"- {b}" for b in bullet_texts)
        
        # Convert back to structured format
        polished_bullets = []
        for line in polished.split("\n"):
            if line.strip():
                text = line.lstrip("- ").strip()
                polished_bullets.append({
                    "text": text,
                    "has_location": "location" in text.lower() or "based" in text.lower(),
                    "has_date": any(year in text for year in [str(y) for y in range(2010, 2030)])
                })
        improved_entry["bullets"] = polished_bullets
    else:
        # Bullet polish: process each bullet individually
        polished_bullets = []
        for bullet in bullet_texts:
            prompt = bullet_polish_prompt(bullet, mode=polish_mode)
            polished_one = ask_llm(prompt, task_type="polish")
            cleaned_one = clean_bullets(polished_one)
            
            if cleaned_one:
                first_line = cleaned_one.split("\n")[0].strip()
                if len(first_line) <= 300:
                    text = first_line.lstrip("- ").strip()
                else:
                    text = bullet
            else:
                text = bullet
            
            polished_bullets.append({
                "text": text,
                "has_location": "location" in text.lower() or "based" in text.lower(),
                "has_date": any(year in text for year in [str(y) for y in range(2010, 2030)])
            })
        
        improved_entry["bullets"] = polished_bullets
    
    return improved_entry
                    

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
    """Append a new experience entry to resume using Mistral structured format."""
    from core.pdf_generator import generate_pdf
    from core.input_parser import parse_resume_with_mistral

    sections = parse_resume_with_mistral(filepath)
    if not sections:
        raise ValueError("Could not parse resume with Mistral parser.")

    cleaned_section = (section or "").strip().lower().replace(" ", "_")
    cleaned_title = (title or "").strip()
    cleaned_bullets = [b.strip().lstrip("-* ") for b in (bullets or []) if b and b.strip()]

    if not cleaned_section:
        raise ValueError("Section is required (e.g., work_experience, projects, leadership)")
    if not cleaned_title:
        raise ValueError("Experience title is required.")
    if not cleaned_bullets:
        raise ValueError("At least one bullet is required.")

    # Create entry in structured format
    new_entry = {
        "position": cleaned_title,
        "company": "",
        "bullets": [
            {
                "text": bullet,
                "has_location": any(keyword in bullet.lower() for keyword in ["location", "based", "city", "office"]),
                "has_date": any(str(y) in bullet for y in range(2010, 2030))
            }
            for bullet in cleaned_bullets
        ]
    }

    # Append to section
    if cleaned_section not in sections:
        sections[cleaned_section] = []
    
    if not isinstance(sections[cleaned_section], list):
        sections[cleaned_section] = []
    
    sections[cleaned_section].append(new_entry)

    destination = output_path or filepath
    generate_pdf(sections, destination)
    return destination

if __name__ == "__main__":
    from core.input_parser import parse_resume_with_mistral
    
    print("=== Testing Output Builder with Structured Format ===\n")
    
    filepath = "samples/resume.txt"
    structured = parse_resume_with_mistral(filepath)
    
    if structured:
        print("Parsing resume...")
        improved_structured = build_resume(structured, None)
        
        print("\nImproved structured resume:")
        print(json.dumps(improved_structured, indent=2))
    else:
        print("Error: Could not parse resume")