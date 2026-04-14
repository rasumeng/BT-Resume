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

# ── RESUME DATA ────────────────────────────────────────────────────────────────

NAME = "Robert Asumeng"

CONTACT = (
    '<link href="mailto:asumengrobert787@gmail.com" color="blue">'
    '<u>asumengrobert787@gmail.com</u></link>'
    ' | 469-594-2623 | '
    '<link href="https://www.linkedin.com/in/robertasumeng/" color="blue">'
    '<u>www.linkedin.com/in/robertasumeng/</u></link>'
    ' | '
    '<link href="https://github.com/rasumeng" color="blue">'
    '<u>github.com/rasumeng</u></link>'
)

EDUCATION = [
    {
        "school": "University of Texas at Arlington",
        "dates": "Aug 2023 - May 2027",
        "detail": "Bachelors of Science in Computer Science | GPA: 3.8 / 4.0",
    }
]

TECHNICAL_SKILLS = [
    ("<b>Programming Languages</b>", "Python, C/C++, SQL, Java, HTML/CSS"),
    ("<b>AI/ML</b>", "LLM Integration, Prompt Engineering, ML Pipelines, Feature Engineering, Model Evaluation"),
    ("<b>Data</b>", "Pandas, NumPy, Scikit-learn, ETL, Data Cleaning, Transformation"),
    ("<b>Tools</b>", "Git, GitHub, Linux, VS Code, Jupyter"),
    ("<b>Soft Skills</b>", "Analytical Thinking, Communication, Leadership, Adaptability, Cross-Functional Collaboration"),
]

WORK_EXPERIENCE = [
    {
        "title": "AI Trainer",
        "company": "Handshake",
        "dates": "Dec 2025 – Present",
        "bullets": [
            "Created and tested 50+ <b>AI prompts</b> to improve model outputs, achieving an average <b>QA rating of 2.72</b> (target: 2.0).",
            "Reviewed AI-generated outputs for logical consistency, identifying errors in 19% of submissions and enhancing overall reliability.",
        ],
    },
    {
        "title": "Data System Engineer",
        "company": "FAPEMPA LLC",
        "dates": "Feb 2023 – Dec 2024",
        "bullets": [
            "Built scalable ETL pipelines for financial data across 10+ sites, improving throughput by <b>40%</b>.",
            "Automated financial reporting tools using Python, reducing data processing time by 70% and increasing reliability by <b>40%</b>.",
            "Developed SQL queries and CTEs to reconcile multi-site data, increasing monthly reporting accuracy by 25%.",
        ],
    },
    {
        "title": "IT Systems & Web Intern",
        "company": "DFW Ghana SDA Church",
        "dates": "Jan 2024 – Dec 2025",
        "bullets": [
            "Automated database operations with Python, reducing manual effort by <b>30%</b> and ensuring fault-tolerant backups.",
            "Built server monitoring and auto-recovery system, achieving <b>99.7% uptime</b> for critical infrastructure.",
        ],
    },
]

PROJECTS = [
    {
        "name": "Beyond The Resume (BTR)",
        "tech": "Python, Ollama, LLaMA 3, Mistral, ReportLab",
        "bullets": [
            "Engineered a <b>local AI resume optimization pipeline</b> using Python and Ollama, implementing smart model routing between Mistral 7B and LLaMA 3 8B to balance speed and output quality across 3 distinct NLP tasks",
            "Built a modular prompt engineering system with iterative refinement, achieving consistent <b>ATS-optimized bullet</b> generation with hallucination prevention across PDF and TXT resume inputs",
            "Developed an <b>end-to-end document processing pipeline</b> supporting PDF parsing, section extraction, LLM-based rewriting, and structured PDF generation — <b>100% offline</b>, no external APIs required",
        ],
    },
    {
        "name": "Housing Price Prediction — End-to-End ML Pipeline",
        "tech": "Python, Pandas, Scikit-learn",
        "bullets": [
            "Built a full ML pipeline to predict residential housing prices using <b>74 structured features</b> from the Kaggle House Prices competition.",
            "Developed modular preprocessing pipelines (imputation, encoding, scaling), handled outliers, and applied LassoCV with 5-fold cross-validation, achieving <b>R² = 0.9186</b> and <b>RMSE = 0.1172</b> on a held-out test set.",
            "Implemented reproducible experimentation workflow with feature selection, regularization tuning, and model evaluation.",
        ],
    },
    {
        "name": "8-Puzzle AI Solver",
        "tech": "Python",
        "bullets": [
            "Implemented 7 search algorithms (A*, Greedy, UCS, BFS, DFS, DLS, IDS) with weighted Manhattan heuristic.",
            "Developed graph-search/tree-search frameworks using priority queues, visited-state hashing, and parent-pointer nodes.",
            "Benchmark: A* expanded 95× fewer nodes than UCS (64 vs 6,068) while preserving optimal solutions.",
        ],
    },
]

LEADERSHIP = [
    {
        "title": "Secretary",
        "org": "UTA ColorStack",
        "dates": "Sep 2025 – Present",
        "bullets": [
            "Built Notion database as single source of truth for 15+ officers; filterable views reduced lookup time by 50%.",
            "Automated roster sync between Slack/Notion for 50 members, standardizing 100+ records and saving 3 hours weekly.",
        ],
    }
]

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

def build_resume(output_path="Robert_Asumeng_Resume.pdf"):
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
    build_resume("Robert_Asumeng_Resume.pdf")
