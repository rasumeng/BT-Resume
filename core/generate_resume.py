"""
Resume PDF Generator - Robert Asumeng
Generates a resume PDF matching the exact format of the original.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import KeepTogether

# ── RESUME DATA (Customizable) ─────────────────────────────────────────────────
# These variables can be populated by the LLM or other sources.
# The structure and data organization remain fixed for consistent PDF generation.

NAME = ""

CONTACT = ""

EDUCATION = []

TECHNICAL_SKILLS = []

WORK_EXPERIENCE = []

PROJECTS = []

LEADERSHIP = []


# ── HELPER FUNCTION: Load Resume Data ──────────────────────────────────────────
def load_resume_data(resume_dict):
    """
    Populate resume variables from a dictionary.
    Expected keys: name, contact, education, technical_skills, work_experience, projects, leadership
    
    Structure:
    - education: list of {school, dates, detail}
    - technical_skills: list of (label, value) tuples
    - work_experience: list of {title, company, dates, bullets[]}
    - projects: list of {name, tech, bullets[]}
    - leadership: list of {title, org, dates, bullets[]}
    """
    global NAME, CONTACT, EDUCATION, TECHNICAL_SKILLS, WORK_EXPERIENCE, PROJECTS, LEADERSHIP
    
    NAME = resume_dict.get("name", "")
    CONTACT = resume_dict.get("contact", "")
    EDUCATION = resume_dict.get("education", [])
    TECHNICAL_SKILLS = resume_dict.get("technical_skills", [])
    WORK_EXPERIENCE = resume_dict.get("work_experience", [])
    PROJECTS = resume_dict.get("projects", [])
    LEADERSHIP = resume_dict.get("leadership", [])

# ── STYLES ─────────────────────────────────────────────────────────────────────

def build_styles():
    base_font = "Times-Roman"
    base_bold = "Times-Bold"
    fs = 10  # base font size

    name_style = ParagraphStyle(
        "Name",
        fontName=base_bold,
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    contact_style = ParagraphStyle(
        "Contact",
        fontName=base_font,
        fontSize=fs - 1,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        fontName=base_bold,
        fontSize=fs,
        spaceBefore=5,
        spaceAfter=1,
        textColor=colors.black,
    )
    school_style = ParagraphStyle(
        "School",
        fontName=base_bold,
        fontSize=fs,
        spaceAfter=0,
    )
    detail_style = ParagraphStyle(
        "Detail",
        fontName=base_font,
        fontSize=fs,
        spaceAfter=3,
    )
    job_title_style = ParagraphStyle(
        "JobTitle",
        fontName=base_bold,
        fontSize=fs,
        spaceAfter=0,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        fontName=base_font,
        fontSize=fs,
        leftIndent=14,
        firstLineIndent=0,
        spaceAfter=2,
        leading=13,
    )
    skill_bullet_style = ParagraphStyle(
        "SkillBullet",
        fontName=base_font,
        fontSize=fs,
        leftIndent=14,
        spaceAfter=2,
        leading=13,
    )
    project_name_style = ParagraphStyle(
        "ProjectName",
        fontName=base_bold,
        fontSize=fs,
        spaceAfter=0,
    )
    return {
        "name": name_style,
        "contact": contact_style,
        "section_header": section_header_style,
        "school": school_style,
        "detail": detail_style,
        "job_title": job_title_style,
        "bullet": bullet_style,
        "skill_bullet": skill_bullet_style,
        "project_name": project_name_style,
    }


# ── HELPERS ────────────────────────────────────────────────────────────────────

def hr():
    return HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceAfter=3, spaceBefore=1)


def two_col_row(left_para, right_text, styles, left_style_key="job_title"):
    """Returns a Table with left-aligned bold text and right-aligned italic dates."""
    right_style = ParagraphStyle(
        "RightDate",
        fontName="Times-Italic",
        fontSize=10,
        alignment=TA_RIGHT,
    )
    data = [[
        Paragraph(left_para if isinstance(left_para, str) else "", styles[left_style_key]),
        Paragraph(f"<i>{right_text}</i>", right_style),
    ]]
    t = Table(data, colWidths=["70%", "30%"])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def bullet_item(text, styles):
    return Paragraph(f"● {text}", styles["bullet"])


# ── BUILD PDF ──────────────────────────────────────────────────────────────────

def build_resume(resume_data=None, output_path="Robert_Asumeng_Resume.pdf"):
    """
    Build and generate a resume PDF.
    
    Args:
        resume_data (dict, optional): Resume data to populate. If provided, loads this data.
                                       Expected keys: name, contact, education, technical_skills,
                                       work_experience, projects, leadership
        output_path (str): Path to save the PDF file.
    """
    if resume_data:
        load_resume_data(resume_data)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    styles = build_styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(NAME, styles["name"]))
    story.append(Paragraph(CONTACT, styles["contact"]))

    # ── Education ─────────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", styles["section_header"]))
    story.append(hr())
    for edu in EDUCATION:
        story.append(two_col_row(edu["school"], edu["dates"], styles, "school"))
        story.append(Paragraph(edu["detail"], styles["detail"]))

    # ── Technical Skills ──────────────────────────────────────────────────────
    story.append(Paragraph("TECHNICAL SKILLS", styles["section_header"]))
    story.append(hr())
    for label, value in TECHNICAL_SKILLS:
        story.append(Paragraph(f"● {label}: {value}", styles["skill_bullet"]))
    story.append(Spacer(1, 3))

    # ── Work Experience ───────────────────────────────────────────────────────
    story.append(Paragraph("WORK EXPERIENCE", styles["section_header"]))
    story.append(hr())
    for job in WORK_EXPERIENCE:
        header_text = f"<b>{job['title']}</b> – {job['company']}"
        story.append(two_col_row(header_text, job["dates"], styles, "job_title"))
        for b in job["bullets"]:
            story.append(bullet_item(b, styles))
        story.append(Spacer(1, 3))

    # ── Projects ──────────────────────────────────────────────────────────────
    story.append(Paragraph("PROJECTS", styles["section_header"]))
    story.append(hr())
    for proj in PROJECTS:
        header = f"<b>{proj['name']}</b> | {proj['tech']}"
        story.append(Paragraph(header, styles["project_name"]))
        for b in proj["bullets"]:
            story.append(bullet_item(b, styles))
        story.append(Spacer(1, 3))

    # ── Leadership ────────────────────────────────────────────────────────────
    story.append(Paragraph("LEADERSHIP", styles["section_header"]))
    story.append(hr())
    for role in LEADERSHIP:
        header_text = f"<b>{role['title']}</b> – {role['org']}"
        story.append(two_col_row(header_text, role["dates"], styles, "job_title"))
        for b in role["bullets"]:
            story.append(bullet_item(b, styles))

    doc.build(story)
    print(f"✅ Resume saved to: {output_path}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING: LLM Resume Parsing & PDF Generation Pipeline")
    print("="*70 + "\n")
    
    import os
    
    # Load the actual PDF resume from the resumes folder
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "resumes", "Roberts_Resume_-_AI.pdf")
    
    print(f"📄 STEP 1: Loading Resume PDF")
    print("-" * 70)
    print(f"Looking for: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: Could not find PDF at {pdf_path}")
        print("\nAvailable files in resumes folder:")
        resumes_dir = os.path.join(os.path.dirname(__file__), "..", "resumes")
        if os.path.exists(resumes_dir):
            for file in os.listdir(resumes_dir):
                print(f"  - {file}")
        else:
            print("  (resumes folder not found)")
        exit(1)
    
    # Extract text from PDF
    from core.input_parser import load_pdf
    
    try:
        print(f"✅ Found PDF file\n")
        print("🔄 Extracting text from PDF...")
        print("-" * 70)
        resume_text = load_pdf(pdf_path)
        print(f"✅ Extracted {len(resume_text)} characters from PDF\n")
        print("Sample of extracted text:")
        print(resume_text[:300] + "...\n")
    except Exception as e:
        print(f"❌ ERROR: Failed to load PDF: {str(e)}")
        exit(1)
    
    # Step 2: Parse resume with LLM
    print("🤖 STEP 2: Parsing Resume with LLM...")
    print("-" * 70)
    
    from core.llm_client import parse_resume_to_pdf_format
    
    try:
        resume_data = parse_resume_to_pdf_format(resume_text)
        
        if not resume_data:
            print("❌ ERROR: LLM parsing returned empty result")
            print("\nTip: Make sure Ollama is running and models are loaded:")
            print("  1. Run 'ollama serve' in a terminal")
            print("  2. Run 'ollama pull mistral:7b' to load the model")
            exit(1)
        
        print("✅ Parse successful!\n")
        
        # Step 3: Display parsed data
        print("📊 STEP 3: Parsed Data Structure")
        print("-" * 70)
        
        print(f"Name: {resume_data.get('name', 'N/A')}")
        print(f"Contact (HTML): {resume_data.get('contact', 'N/A')[:80]}...")
        
        education = resume_data.get('education', [])
        print(f"\nEducation entries: {len(education)}")
        for i, edu in enumerate(education, 1):
            print(f"  {i}. {edu.get('school')} ({edu.get('dates')})")
        
        skills = resume_data.get('technical_skills', [])
        print(f"\nSkill categories: {len(skills)}")
        for i, (label, value) in enumerate(skills, 1):
            # Remove HTML tags for display
            clean_label = label.replace('<b>', '').replace('</b>', '')
            print(f"  {i}. {clean_label}: {value[:50]}...")
        
        work = resume_data.get('work_experience', [])
        print(f"\nWork experience entries: {len(work)}")
        for i, job in enumerate(work, 1):
            print(f"  {i}. {job.get('title')} at {job.get('company')} ({len(job.get('bullets', []))} bullets)")
        
        projects = resume_data.get('projects', [])
        print(f"\nProjects: {len(projects)}")
        for i, proj in enumerate(projects, 1):
            print(f"  {i}. {proj.get('name')} ({len(proj.get('bullets', []))} bullets)")
        
        leadership = resume_data.get('leadership', [])
        print(f"\nLeadership roles: {len(leadership)}")
        for i, role in enumerate(leadership, 1):
            print(f"  {i}. {role.get('title')} at {role.get('org')}")
        
        # Step 4: Generate PDF from parsed data
        print("\n\n📝 STEP 4: Generating PDF from Parsed Data")
        print("-" * 70)
        
        output_filename = "test_generated_resume.pdf"
        build_resume(resume_data, output_filename)
        
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename) / 1024  # KB
            print(f"✅ PDF generated successfully: {output_filename} ({file_size:.1f} KB)")
            print("\n" + "="*70)
            print("✨ PIPELINE TEST PASSED!")
            print("="*70)
            print("\nThe pipeline works as follows:")
            print(f"1. Loaded PDF from: {pdf_path}")
            print("2. Extracted text from PDF")
            print("3. LLM parsed resume text into structured JSON")
            print("4. PDF was generated from the structured data")
            print("\n" + "="*70 + "\n")
        else:
            print(f"❌ ERROR: PDF file was not created")
    
    except Exception as e:
        print(f"❌ ERROR during pipeline test: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Ensure mistral:7b is loaded: ollama pull mistral:7b")
        print("3. Check internet connection if pulling models")
        print("4. Ensure Roberts_Resume_-_AI.pdf exists in resumes folder")
        exit(1)
