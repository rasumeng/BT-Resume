"""
Resume PDF Generator (V2)

Generates professional resume PDFs from ResumData objects.
Uses Jake's Resume template styling with ReportLab.

Workflow: ResumData -> JSON -> PDF
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, 
    TableStyle, PageBreak
)

from .resume_model import ResumData


# ============================================================================
# PDF CONFIGURATION & STYLING
# ============================================================================

# Page settings (inches)
PAGE_LEFT_MARGIN = 0.5
PAGE_RIGHT_MARGIN = 0.5
PAGE_TOP_MARGIN = 0.5
PAGE_BOTTOM_MARGIN = 0.5

# Convert to points (1 inch = 72 points)
PAGE_WIDTH = 8.5
PAGE_HEIGHT = 11
USABLE_WIDTH = (PAGE_WIDTH - PAGE_LEFT_MARGIN - PAGE_RIGHT_MARGIN) * 72

# Font sizes
HEADER_NAME_FONT_SIZE = 20  # Candidate name - larger serif
HEADER_INFO_FONT_SIZE = 9   # Contact info line
SECTION_HEADER_FONT_SIZE = 11  # WORK EXPERIENCE, EDUCATION, etc.
ENTRY_TITLE_FONT_SIZE = 11  # Position, Degree, Project
ENTRY_COMPANY_FONT_SIZE = 10  # Company, School, Organization
BULLET_FONT_SIZE = 10
SKILL_CATEGORY_FONT_SIZE = 10

# Spacing (points)
HEADER_NAME_SPACE_AFTER = 3  # Space after name to separate from contact
HEADER_INFO_SPACE_AFTER = 12  # Space after contact info before first section
SECTION_HEADER_SPACE_BEFORE = 6  # Space before section header
SECTION_HEADER_SPACE_AFTER = 2  # Space after section header line
SECTION_DIVIDER_SPACE_AFTER = 4
ENTRY_SPACE_BEFORE = 1  # Space before entry
ENTRY_SPACE_AFTER = 0  # Space after entry
BULLET_LEFT_INDENT = 14
BULLET_FIRST_LINE_INDENT = -14
BETWEEN_ENTRIES_SPACE = 4  # Space between entries

# Colors
COLOR_BLACK = colors.HexColor("#000000")
COLOR_DARK_GRAY = colors.HexColor("#333333")
COLOR_GRAY = colors.HexColor("#666666")


# ============================================================================
# PARAGRAPH STYLES
# ============================================================================

def create_styles():
    """Create all paragraph styles for the resume"""
    return {
        "name": ParagraphStyle(
            "name",
            fontName="Times-Bold",
            fontSize=HEADER_NAME_FONT_SIZE,
            alignment=TA_CENTER,
            textColor=COLOR_BLACK,
            spaceAfter=HEADER_NAME_SPACE_AFTER,
        ),
        "contact_info": ParagraphStyle(
            "contact_info",
            fontName="Times-Roman",
            fontSize=HEADER_INFO_FONT_SIZE,
            alignment=TA_CENTER,
            textColor=COLOR_GRAY,
            spaceAfter=HEADER_INFO_SPACE_AFTER,
            leading=10,  # Line height for better wrapping
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName="Times-Bold",
            fontSize=SECTION_HEADER_FONT_SIZE,
            textTransform="uppercase",
            spaceBefore=SECTION_HEADER_SPACE_BEFORE,
            spaceAfter=SECTION_HEADER_SPACE_AFTER,
            textColor=COLOR_BLACK,
            alignment=TA_LEFT,
        ),
        "entry_title": ParagraphStyle(
            "entry_title",
            fontName="Times-Bold",
            fontSize=ENTRY_TITLE_FONT_SIZE,
            textColor=COLOR_BLACK,
            spaceAfter=0,
            alignment=TA_LEFT,
        ),
        "entry_subtitle": ParagraphStyle(
            "entry_subtitle",
            fontName="Times-Italic",
            fontSize=ENTRY_COMPANY_FONT_SIZE,
            textColor=COLOR_DARK_GRAY,
            spaceAfter=2,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Times-Roman",
            fontSize=BULLET_FONT_SIZE,
            leftIndent=BULLET_LEFT_INDENT,
            firstLineIndent=BULLET_FIRST_LINE_INDENT,
            spaceAfter=3,
            textColor=COLOR_DARK_GRAY,
            alignment=TA_LEFT,
        ),
        "skill_category": ParagraphStyle(
            "skill_category",
            fontName="Times-Bold",
            fontSize=SKILL_CATEGORY_FONT_SIZE,
            textColor=COLOR_BLACK,
            spaceAfter=0,
            alignment=TA_LEFT,
        ),
        "skill_items": ParagraphStyle(
            "skill_items",
            fontName="Times-Roman",
            fontSize=BULLET_FONT_SIZE,
            textColor=COLOR_DARK_GRAY,
            spaceAfter=2,
            alignment=TA_LEFT,
        ),
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _safe_html(text: str) -> str:
    """Escape HTML special characters to prevent ReportLab errors"""
    if not text:
        return ""
    import html
    return html.escape(str(text))


def _format_date_range(start_date: str, end_date: str) -> str:
    """Format start and end dates"""
    dates = []
    if start_date:
        dates.append(start_date)
    if end_date:
        dates.append(end_date)
    return " – ".join(dates) if dates else ""


# ============================================================================
# PDF BUILDING BLOCKS
# ============================================================================

def _build_header(resume: ResumData, styles: dict) -> list:
    """Build the header section with name and contact info"""
    elements = []
    
    # Name
    name = _safe_html(resume.contact.name)
    elements.append(Paragraph(name, styles["name"]))
    
    # Contact info line
    contact_line = resume.contact.get_contact_line()
    if contact_line:
        elements.append(Paragraph(_safe_html(contact_line), styles["contact_info"]))
    
    return elements


def _build_section_header(section_title: str, styles: dict) -> list:
    """Build a section header with divider line"""
    elements = []
    
    # Section title
    title_para = Paragraph(section_title.upper(), styles["section_header"])
    elements.append(title_para)
    
    # Horizontal divider
    divider = HRFlowable(
        width="100%",
        thickness=0.5,
        lineCap="round",
        color=COLOR_BLACK,
        spaceBefore=0,
        spaceAfter=SECTION_DIVIDER_SPACE_AFTER,
    )
    elements.append(divider)
    
    return elements


def _build_work_experience_entry(entry, styles: dict) -> list:
    """Build a work experience entry"""
    elements = []
    
    # Title and date row
    title_parts = []
    if entry.position:
        title_parts.append(_safe_html(entry.position))
    
    date_str = _format_date_range(entry.start_date, entry.end_date)
    
    # Create 2-column table for title and date
    if title_parts:
        title_cell = Paragraph(" ".join(title_parts), styles["entry_title"])
        date_cell = Paragraph(date_str or "", styles["entry_title"]) if date_str else None
        
        if date_cell:
            title_table = Table(
                [[title_cell, date_cell]],
                colWidths=[USABLE_WIDTH * 0.65, USABLE_WIDTH * 0.35],
                hAlign=TA_LEFT,
            )
            title_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            elements.append(title_table)
        else:
            elements.append(title_cell)
    
    # Subtitle row (company and location)
    subtitle_parts = []
    if entry.company:
        subtitle_parts.append(_safe_html(entry.company))
    if entry.location:
        subtitle_parts.append(_safe_html(entry.location))
    
    if subtitle_parts:
        subtitle = " | ".join(subtitle_parts)
        elements.append(Paragraph(subtitle, styles["entry_subtitle"]))
    
    # Bullets
    if entry.bullets:
        for bullet in entry.bullets:
            bullet_text = _safe_html(bullet.text)
            elements.append(Paragraph(bullet_text, styles["bullet"]))
    
    return elements


def _build_education_entry(entry, styles: dict) -> list:
    """Build an education entry"""
    elements = []
    
    # Degree and date
    degree_parts = []
    if entry.degree:
        degree_parts.append(_safe_html(entry.degree))
    
    if degree_parts:
        degree_text = " ".join(degree_parts)
        if entry.date:
            degree_cell = Paragraph(degree_text, styles["entry_title"])
            date_cell = Paragraph(_safe_html(entry.date), styles["entry_title"])
            
            title_table = Table(
                [[degree_cell, date_cell]],
                colWidths=[USABLE_WIDTH * 0.65, USABLE_WIDTH * 0.35],
                hAlign=TA_LEFT,
            )
            title_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),

            ]))
            elements.append(title_table)
        else:
            elements.append(Paragraph(degree_text, styles["entry_title"]))
    
    # School and location
    school_parts = []
    if entry.school:
        school_parts.append(_safe_html(entry.school))
    if entry.location:
        school_parts.append(_safe_html(entry.location))
    
    if school_parts:
        school_text = " | ".join(school_parts)
        elements.append(Paragraph(school_text, styles["entry_subtitle"]))
    
    # Details
    if entry.details:
        for detail in entry.details:
            if isinstance(detail, dict) and detail.get("text"):
                detail_text = _safe_html(detail["text"])
            else:
                detail_text = _safe_html(str(detail))
            elements.append(Paragraph(detail_text, styles["bullet"]))
    
    return elements


def _build_project_entry(entry, styles: dict) -> list:
    """Build a project entry"""
    elements = []
    
    # Project name and date
    if entry.name:
        name_text = _safe_html(entry.name)
        
        if entry.date:
            name_cell = Paragraph(name_text, styles["entry_title"])
            date_cell = Paragraph(_safe_html(entry.date), styles["entry_title"])
            
            title_table = Table(
                [[name_cell, date_cell]],
                colWidths=[USABLE_WIDTH * 0.65, USABLE_WIDTH * 0.35],
                hAlign=TA_LEFT,
            )
            title_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),

            ]))
            elements.append(title_table)
        else:
            elements.append(Paragraph(name_text, styles["entry_title"]))
    
    # Technologies and location
    info_parts = []
    if entry.technologies:
        info_parts.append(_safe_html(entry.technologies))
    if entry.location:
        info_parts.append(_safe_html(entry.location))
    
    if info_parts:
        info_text = " | ".join(info_parts)
        elements.append(Paragraph(info_text, styles["entry_subtitle"]))
    
    # Bullets
    if entry.bullets:
        for bullet in entry.bullets:
            bullet_text = _safe_html(bullet.text)
            elements.append(Paragraph(bullet_text, styles["bullet"]))
    
    return elements


def _build_leadership_entry(entry, styles: dict) -> list:
    """Build a leadership/activities entry"""
    elements = []
    
    # Title and date
    if entry.title:
        title_text = _safe_html(entry.title)
        
        if entry.date:
            title_cell = Paragraph(title_text, styles["entry_title"])
            date_cell = Paragraph(_safe_html(entry.date), styles["entry_title"])
            
            title_table = Table(
                [[title_cell, date_cell]],
                colWidths=[USABLE_WIDTH * 0.65, USABLE_WIDTH * 0.35],
                hAlign=TA_LEFT,
            )
            title_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),

            ]))
            elements.append(title_table)
        else:
            elements.append(Paragraph(title_text, styles["entry_title"]))
    
    # Organization and location
    org_parts = []
    if entry.organization:
        org_parts.append(_safe_html(entry.organization))
    if entry.location:
        org_parts.append(_safe_html(entry.location))
    
    if org_parts:
        org_text = " | ".join(org_parts)
        elements.append(Paragraph(org_text, styles["entry_subtitle"]))
    
    # Bullets
    if entry.bullets:
        for bullet in entry.bullets:
            bullet_text = _safe_html(bullet.text)
            elements.append(Paragraph(bullet_text, styles["bullet"]))
    
    return elements


def _build_skills_section(resume: ResumData, styles: dict) -> list:
    """Build the skills section"""
    elements = []
    
    for skill in resume.skills:
        # Category
        if skill.category:
            elements.append(Paragraph(_safe_html(skill.category), styles["skill_category"]))
        
        # Items (comma-separated)
        if skill.items:
            items_text = ", ".join([_safe_html(item) for item in skill.items])
            elements.append(Paragraph(items_text, styles["skill_items"]))
    
    return elements


# ============================================================================
# MAIN PDF GENERATOR FUNCTION
# ============================================================================

def generate_pdf(resume: ResumData, output_path: str):
    """
    Generate a professional resume PDF from ResumData object.
    
    Args:
        resume: ResumData object with all resume information
        output_path: Path where PDF should be saved
    
    Returns:
        None (writes PDF to disk)
    """
    # Create document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=PAGE_LEFT_MARGIN * 72,
        rightMargin=PAGE_RIGHT_MARGIN * 72,
        topMargin=PAGE_TOP_MARGIN * 72,
        bottomMargin=PAGE_BOTTOM_MARGIN * 72,
    )
    
    # Create styles
    styles = create_styles()
    
    # Build document content
    story = []
    
    # ===== HEADER =====
    story.extend(_build_header(resume, styles))
    
    # ===== EDUCATION =====
    if resume.education:
        story.extend(_build_section_header("Education", styles))
        
        for idx, entry in enumerate(resume.education):
            story.extend(_build_education_entry(entry, styles))
            
            # Add spacing between entries
            if idx + 1 < len(resume.education):
                story.append(Spacer(1, BETWEEN_ENTRIES_SPACE))
    
    # ===== WORK EXPERIENCE =====
    if resume.work_experience:
        story.extend(_build_section_header("Work Experience", styles))
        
        for idx, entry in enumerate(resume.work_experience):
            story.extend(_build_work_experience_entry(entry, styles))
            
            # Add spacing between entries
            if idx + 1 < len(resume.work_experience):
                story.append(Spacer(1, BETWEEN_ENTRIES_SPACE))
    
    # ===== PROJECTS =====
    if resume.projects:
        story.extend(_build_section_header("Projects", styles))
        
        for idx, entry in enumerate(resume.projects):
            story.extend(_build_project_entry(entry, styles))
            
            # Add spacing between entries
            if idx + 1 < len(resume.projects):
                story.append(Spacer(1, BETWEEN_ENTRIES_SPACE))
    
    # ===== LEADERSHIP =====
    if resume.leadership:
        story.extend(_build_section_header("Leadership", styles))
        
        for idx, entry in enumerate(resume.leadership):
            story.extend(_build_leadership_entry(entry, styles))
            
            # Add spacing between entries
            if idx + 1 < len(resume.leadership):
                story.append(Spacer(1, BETWEEN_ENTRIES_SPACE))
    
    # ===== SKILLS =====
    if resume.skills:
        story.extend(_build_section_header("Skills", styles))
        story.extend(_build_skills_section(resume, styles))
    
    # Build the PDF
    doc.build(story)
    
    print(f"✓ PDF generated successfully: {output_path}")
