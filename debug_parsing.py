from core.input_parser import load_pdf, parse_section
text = load_pdf('samples/resume.pdf')
lines = text.split('\n')

print('=== RAW PDF EXTRACTION (all lines) ===')
for i, line in enumerate(lines):
    marker = ' <-- FOUND JAVA DEV' if 'java application' in line.lower() else ''
    marker = ' <-- FOUND FIN OPS' if 'financial' in line.lower() else marker
    marker = ' <-- FOUND PROJECTS' if line.strip().upper() == 'PROJECTS' else marker
    print(f'{i:3d}: {line[:120]}{marker}')

print("\n\n=== SECTION DETECTION ===")
sections = parse_section(text)
for section_name, content in sections.items():
    if section_name == '_CONTACT':
        print(f"\n{section_name}: {content}")
    else:
        content_preview = content[:150].replace('\n', ' ') if isinstance(content, str) else str(content)[:150]
        print(f"\n{section_name}: {content_preview}...")
