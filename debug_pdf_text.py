"""Debug script to see extracted PDF text"""

import pdfplumber

pdf_path = "resumes/Roberts_Resume_-_AI.pdf"

print("=" * 70)
print(f"DEBUGGING PDF TEXT EXTRACTION: {pdf_path}")
print("=" * 70)

with pdfplumber.open(pdf_path) as pdf:
    first_page = pdf.pages[0]
    text = first_page.extract_text()
    
    print("\nFull extracted text:")
    print("-" * 70)
    print(text)
    print("-" * 70)
    
    # Look for education section
    print("\nSearching for EDUCATION section...")
    if "EDUCATION" in text.upper():
        print("✓ Found 'EDUCATION' in text")
        
        # Find its location and context
        upper_text = text.upper()
        edu_pos = upper_text.find("EDUCATION")
        context = text[max(0, edu_pos-50):min(len(text), edu_pos+300)]
        print(f"\nContext around EDUCATION (position {edu_pos}):")
        print("---")
        print(repr(context))
        print("---")
    else:
        print("✗ 'EDUCATION' not found in text")
        print("\nAll section-like headers found:")
        for line in text.split('\n'):
            if line.strip() and line.strip().isupper() and len(line.strip()) < 50:
                print(f"  - {repr(line)}")
