from input_parser import parse_section, parse_subsections
from prompts import bullet_polish_prompt
from llm_client import ask_llm

SECTIONS_TO_POLISH = ["WORK EXPERIENCE", "PROJECTS", "LEADERSHIP"]


def build_resume(sections: dict) -> dict:
    improved_sections = {}
    for section, content in sections.items():
        if section in SECTIONS_TO_POLISH:
            improved_sections[section] = polish_section(content)
        else:
            improved_sections[section] = content
    return improved_sections    

def polish_section(section_text: str) -> str:
    subsections = parse_subsections(section_text)
    result = ""
    for sub in subsections:
        titles = sub["title"]
        bullets = sub["bullets"]
        
        # Join the bullets into one string and send to AI
        bullets_text = "\n".join(bullets)
        prompt = bullet_polish_prompt(bullets_text)
        polished = ask_llm(prompt)
        polished = clean_bullets(polished)

        result += titles + "\n"
        result += polished + "\n"
        result += "\n"

    return result.strip()
                    

def clean_bullets(text: str) -> str:
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            # Remove leading numbers like "1." "2." etc
            if line[0].isdigit() and line[1] in ".):":
                line = "- " + line[2:].strip()
            if not line.startswith("-"):
                line = "- " + line
            cleaned.append(line)
    return "\n".join(cleaned)

if __name__ == "__main__":
    from input_parser import load_resume
    
    text = load_resume("samples/resume.txt")
    sections = parse_section(text)
    improved = build_resume(sections)

    # improved = build_resume(sections)
    for header, content in improved.items():
        print(f"--- {header} ---")
        print(content)
        print()
