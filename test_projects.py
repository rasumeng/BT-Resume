from core.input_parser import load_pdf, parse_section, parse_subsections

text = load_pdf("samples/resume.pdf")
sections = parse_section(text)

print("=== PROJECTS PARSED ===\n")
if "PROJECTS" in sections:
    subsections = parse_subsections(sections["PROJECTS"], "PROJECTS")
    for i, sub in enumerate(subsections, 1):
        print(f"{i}. {sub['title']}")
        for j, bullet in enumerate(sub['bullets'], 1):
            print(f"   {j}. {bullet[:100]}{'...' if len(bullet) > 100 else ''}")
        print()
