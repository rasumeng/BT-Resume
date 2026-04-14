import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# ============================================================================
# JAKE'S RESUME TEMPLATE STYLING
# Replicates the professional design of Jake's Resume LaTeX template
# ============================================================================

# Page margins
PAGE_LEFT_MARGIN = 0.5
PAGE_RIGHT_MARGIN = 0.5
PAGE_TOP_MARGIN = 0.5
PAGE_BOTTOM_MARGIN = 0.5

# Header styling (name and contact)
HEADER_NAME_FONT_SIZE = 24  # Large, bold name
HEADER_INFO_FONT_SIZE = 10  # Contact info

# Section styling
SECTION_HEADER_FONT_SIZE = 11
SECTION_HEADER_SPACE_BEFORE = 8
SECTION_HEADER_SPACE_AFTER = 6

# Entry styling
ENTRY_TITLE_FONT_SIZE = 11
ENTRY_SUBTITLE_FONT_SIZE = 10
ENTRY_DATE_FONT_SIZE = 10
BULLET_FONT_SIZE = 10

# Spacing
ENTRY_SPACE_BEFORE = 6
ENTRY_SPACE_AFTER = 2
BULLET_LEFT_INDENT = 14
BULLET_FIRST_LINE_INDENT = -8

PAGE_WIDTH = 8.5
USABLE_WIDTH = (PAGE_WIDTH - PAGE_LEFT_MARGIN - PAGE_RIGHT_MARGIN) * 72

# Section order for structured format from Mistral
SECTION_ORDER = [
    "education",
    "work_experience",
    "projects",
    "skills",
    "leadership",
    "certifications",
]


def _build_entry_title_from_structured(entry: dict) -> str:
    """Build a formatted title from a structured entry dict."""
    parts = []
    
    if entry.get("position"):
        parts.append(entry["position"])
    
    if entry.get("company"):
        parts.append(entry["company"])
    
    title = " – ".join(parts) if parts else ""
    
    if entry.get("location") and entry.get("location") not in title:
        title += f" | {entry['location']}"
    
    return title


def _build_entry_date_from_structured(entry: dict) -> str:
    """Build a formatted date range from a structured entry."""
    parts = []
    
    if entry.get("start_date"):
        parts.append(entry["start_date"])
    
    if entry.get("end_date"):
        parts.append(entry["end_date"])
    
    if parts:
        return " – ".join(parts)
    
    return ""


def _section_name_to_title(section_name: str) -> str:
    """Convert section name from lowercase_with_underscores to Title Case."""
    return section_name.replace("_", " ").upper()


def generate_pdf(sections: dict, output_path: str, name: str = "", email: str = "", 
                phone: str = "", linkedin: str = "", github: str = ""):
    """
    Generate PDF from structured resume sections using Jake's Resume template style.
    
    Args:
        sections: Structured resume sections dict from Mistral parser
        output_path: Path to write PDF to
        name: User's full name (optional, extracted from sections if not provided)
        email: Email address
        phone: Phone number
        linkedin: LinkedIn URL
        github: GitHub URL
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=PAGE_LEFT_MARGIN * 72,
        rightMargin=PAGE_RIGHT_MARGIN * 72,
        topMargin=PAGE_TOP_MARGIN * 72,
        bottomMargin=PAGE_BOTTOM_MARGIN * 72,
    )

    # Define Jake's Resume styles
    name_style = ParagraphStyle(
        "name",
        fontName="Helvetica-Bold",
        fontSize=HEADER_NAME_FONT_SIZE,
        alignment=TA_CENTER,
        spaceAfter=3,
    )
    
    contact_style = ParagraphStyle(
        "contact",
        fontName="Helvetica",
        fontSize=HEADER_INFO_FONT_SIZE,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    
    section_header_style = ParagraphStyle(
        "section_header",
        fontName="Helvetica-Bold",
        fontSize=SECTION_HEADER_FONT_SIZE,
        textTransform="uppercase",
        spaceBefore=SECTION_HEADER_SPACE_BEFORE,
        spaceAfter=SECTION_HEADER_SPACE_AFTER,
        alignment=TA_LEFT,
    )
    
    entry_title_style = ParagraphStyle(
        "entry_title",
        fontName="Helvetica-Bold",
        fontSize=ENTRY_TITLE_FONT_SIZE,
        spaceAfter=1,
        alignment=TA_LEFT,
    )
    
    entry_subtitle_style = ParagraphStyle(
        "entry_subtitle",
        fontName="Helvetica-Oblique",
        fontSize=ENTRY_SUBTITLE_FONT_SIZE,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    
    bullet_style = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=BULLET_FONT_SIZE,
        leftIndent=BULLET_LEFT_INDENT,
        firstLineIndent=BULLET_FIRST_LINE_INDENT,
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    
    story = []

    # ========== HEADER SECTION ==========
    # Extract or use provided name
    if not name:
        header_block = sections.get("_HEADER", "")
        if header_block:
            header_lines = [line.strip() for line in header_block.split("\n") if line.strip()]
            if header_lines:
                name = _extract_name_from_header(header_lines[0])
    
    if name:
        story.append(Paragraph(_safe(name), name_style))
    
    # Build contact info line
    contact_parts = []
    if phone:
        contact_parts.append(_safe(phone))
    if email:
        contact_parts.append(_safe(email))
    if linkedin:
        contact_parts.append(_safe(linkedin))
    if github:
        contact_parts.append(_safe(github))
    
    # Fallback to _CONTACT section if no contact info provided
    if not contact_parts:
        contact_info = sections.get("_CONTACT", {})
        if isinstance(contact_info, dict):
            if contact_info.get("phone"):
                contact_parts.append(_safe(contact_info["phone"]))
            if contact_info.get("email"):
                contact_parts.append(_safe(contact_info["email"]))
            if contact_info.get("linkedin"):
                contact_parts.append(_safe(contact_info["linkedin"]))
            if contact_info.get("github"):
                contact_parts.append(_safe(contact_info["github"]))
    
    if contact_parts:
        contact_line = " | ".join(contact_parts)
        story.append(Paragraph(contact_line, contact_style))
    
    # ========== SECTIONS ==========
    # Build ordered sections
    ordered_sections = []
    for section_name in SECTION_ORDER:
        if section_name in sections and section_name != "_HEADER":
            ordered_sections.append((section_name, sections[section_name]))

    # Add any non-standard sections
    for section_name, entries in sections.items():
        if section_name == "_HEADER" or section_name == "_CONTACT" or section_name in SECTION_ORDER:
            continue
        ordered_sections.append((section_name, entries))

    # Render each section
    for section_name, entries in ordered_sections:
        if section_name == "_HEADER" or not entries:
            continue
        
        if not isinstance(entries, list):
            continue

        section_title = _section_name_to_title(section_name)
        
        # Section header with line
        story.append(Paragraph(section_title, section_header_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                lineCap="round",
                color=colors.HexColor("#000000"),
                spaceBefore=0,
                spaceAfter=6,
            )
        )

        # Render entries
        for entry_idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            
            story.append(_build_entry_from_json(entry, entry_title_style, entry_subtitle_style, bullet_style))
            
            # Spacing between entries
            if entry_idx + 1 < len(entries):
                story.append(Spacer(1, 4))

    doc.build(story)


def _build_entry_from_json(entry: dict, title_style, subtitle_style, bullet_style):
    """
    Build entry content from JSON data.
    Returns a table containing the entry structure.
    """
    from reportlab.platypus import Table, TableStyle
    
    rows = []
    
    # Title row (position/school and date)
    title = entry.get("position") or entry.get("title") or entry.get("school") or entry.get("name") or ""
    date_str = ""
    if entry.get("start_date") or entry.get("end_date"):
        dates = []
        if entry.get("start_date"):
            dates.append(entry.get("start_date"))
        if entry.get("end_date"):
            dates.append(entry.get("end_date"))
        date_str = " – ".join(dates)
    
    if title:
        title_para = Paragraph(_safe(title), title_style)
        if date_str:
            date_para = Paragraph(_safe(date_str), title_style)
            rows.append([title_para, date_para])
        else:
            rows.append([title_para, ""])
    
    # Subtitle row (company/degree and location)
    company = entry.get("company") or entry.get("organization") or ""
    degree = entry.get("degree") or ""
    location = entry.get("location") or ""
    
    subtitle_text = company or degree
    if subtitle_text or location:
        subtitle_para = Paragraph(_safe(subtitle_text), subtitle_style)
        location_para = Paragraph(_safe(location), subtitle_style)
        rows.append([subtitle_para, location_para])
    
    # Bullets
    if "bullets" in entry and isinstance(entry["bullets"], list):
        for bullet in entry["bullets"]:
            if isinstance(bullet, dict):
                bullet_text = bullet.get("text", "")
            else:
                bullet_text = str(bullet).strip()
            
            if bullet_text:
                bullet_para = Paragraph(f"• {_safe(bullet_text)}", bullet_style)
                rows.append([bullet_para, ""])
    
    if not rows:
        return Spacer(1, 1)
    
    # Create table with proper column widths
    col_width_left = USABLE_WIDTH * 0.65
    col_width_right = USABLE_WIDTH * 0.35
    
    entry_table = Table(rows, colWidths=[col_width_left, col_width_right])
    entry_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    return entry_table


def _safe(value: str) -> str:
    """Escape HTML special characters."""
    return html.escape((value or "").strip())


def _extract_name_from_header(line: str) -> str:
    """Extract name from a header line."""
    first_part = line.split("|")[0].split("@")[0].strip()
    words = first_part.split()
    name_words = []
    
    for word in words:
        if not all(c.isalpha() or c.isspace() for c in word):
            break
        name_words.append(word)
    
    extracted = " ".join(name_words)
    if 2 <= len(name_words) <= 3 and _is_simple_name(extracted):
        return extracted
    
    return ""


def _is_simple_name(line: str) -> bool:
    """Check if a line is a simple name."""
    stripped = line.strip()
    if not stripped:
        return False
    
    if not all(c.isalpha() or c.isspace() for c in stripped):
        return False
    
    words = stripped.split()
    if not (2 <= len(words) <= 3):
        return False
    
    return all(word and word[0].isupper() for word in words)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from core.input_parser import parse_resume_with_mistral

    filepath = "samples/resume.txt"
    sections = parse_resume_with_mistral(filepath)
    
    if sections:
        generate_pdf(
            sections=sections,
            output_path="outputs/test_resume_jakes_style.pdf",
            name="Jake Ryan",
            email="jake@su.edu",
            phone="123-456-7890",
            linkedin="https://linkedin.com/in/jake",
            github="https://github.com/jake"
        )
        print("✅ PDF generated successfully!")
        print("   Saved to: outputs/test_resume_jakes_style.pdf")
    else:
        print("❌ Error parsing resume")
