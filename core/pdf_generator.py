import html
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# Centralized style knobs for your resume look-and-feel.
PAGE_LEFT_MARGIN = 0.5
PAGE_RIGHT_MARGIN = 0.5
PAGE_TOP_MARGIN = 0.42
PAGE_BOTTOM_MARGIN = 0.42

HEADER_NAME_FONT_SIZE = 15
HEADER_INFO_FONT_SIZE = 9.3

SECTION_HEADER_FONT_SIZE = 10.6
SECTION_BODY_FONT_SIZE = 9.9
SECTION_LEADING = 12.3
BULLET_INDENT = 11

SECTION_TOP_SPACE = 0.005
SECTION_BOTTOM_SPACE = 0.085
HEADER_BOTTOM_SPACE = 0.055

PAGE_WIDTH = 8.5
USABLE_WIDTH = (PAGE_WIDTH - PAGE_LEFT_MARGIN - PAGE_RIGHT_MARGIN) * 72  # 7.5 inches = 540 points

# Section order for structured format from Mistral
SECTION_ORDER = [
    "education",
    "work_experience",
    "projects",
    "skills",
    "leadership",
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


def generate_pdf(sections: dict, output_path: str):
    """
    Generate PDF from structured resume sections (Mistral format).
    
    Args:
        sections: Structured resume sections dict from Mistral parser
        output_path: Path to write PDF to
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=PAGE_LEFT_MARGIN * 72,
        rightMargin=PAGE_RIGHT_MARGIN * 72,
        topMargin=PAGE_TOP_MARGIN * 72,
        bottomMargin=PAGE_BOTTOM_MARGIN * 72,
    )

    # Define styles
    header_style = ParagraphStyle(
        "section_header",
        fontName="Helvetica-Bold",
        fontSize=SECTION_HEADER_FONT_SIZE,
        leading=SECTION_HEADER_FONT_SIZE + 1,
        spaceBefore=0,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "entry_body",
        fontName="Helvetica",
        fontSize=SECTION_BODY_FONT_SIZE,
        leading=SECTION_LEADING,
        spaceAfter=0,
        alignment=TA_LEFT,
    )
    bullet_style = ParagraphStyle(
        "entry_bullet",
        parent=body_style,
        leftIndent=BULLET_INDENT,
        firstLineIndent=-8,
        spaceAfter=3,
    )
    top_name_style = ParagraphStyle(
        "top_name",
        fontName="Helvetica-Bold",
        fontSize=HEADER_NAME_FONT_SIZE,
        leading=HEADER_NAME_FONT_SIZE + 1,
        alignment=TA_CENTER,
        spaceAfter=1,
    )
    top_info_style = ParagraphStyle(
        "top_info",
        fontName="Helvetica",
        fontSize=HEADER_INFO_FONT_SIZE,
        leading=HEADER_INFO_FONT_SIZE + 1.6,
        alignment=TA_CENTER,
        spaceAfter=1,
    )

    story = []

    # Extract contact information if available
    contact_info = sections.get("_CONTACT", {})
    if isinstance(contact_info, dict) and contact_info:
        contact_line_parts = []
        if contact_info.get("email"):
            contact_line_parts.append(contact_info["email"])
        if contact_info.get("phone"):
            contact_line_parts.append(contact_info["phone"])
        if contact_info.get("linkedin"):
            contact_line_parts.append(contact_info["linkedin"])
        if contact_info.get("github"):
            contact_line_parts.append(contact_info["github"])
        
        if contact_line_parts:
            header_block = sections.get("_HEADER", "")
            if header_block:
                header_lines = [line.strip() for line in header_block.split("\n") if line.strip()]
                if header_lines:
                    extracted_name = _extract_name_from_header(header_lines[0])
                    if extracted_name:
                        story.append(Paragraph(f"<b>{_safe(extracted_name)}</b>", top_name_style))
                        story.append(Spacer(1, 6))
                        story.append(Paragraph(_safe(" | ".join(contact_line_parts)), top_info_style))
                        story.append(Spacer(1, HEADER_BOTTOM_SPACE * 72))

    # Build ordered sections
    ordered_sections = []
    for section_name in SECTION_ORDER:
        if section_name in sections and section_name != "_HEADER":
            ordered_sections.append((section_name, sections[section_name]))

    for section_name, entries in sections.items():
        if section_name == "_HEADER" or section_name == "_CONTACT" or section_name in SECTION_ORDER:
            continue
        ordered_sections.append((section_name, entries))

    # Render each section
    for section_name, entries in ordered_sections:
        if section_name == "_HEADER" or not entries:
            continue
        
        # Skip if not a list
        if not isinstance(entries, list):
            continue

        section_title = _section_name_to_title(section_name)
        
        story.append(Spacer(1, SECTION_TOP_SPACE * 72))
        story.append(Paragraph(section_title, header_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                lineCap="round",
                color=colors.HexColor("#2F2F2F"),
                spaceBefore=0,
                spaceAfter=3,
            )
        )

        # Render entries
        for entry_idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            
            # Build entry title and date
            title = _build_entry_title_from_structured(entry)
            date_str = _build_entry_date_from_structured(entry)
            
            if title:
                if date_str:
                    # Use two-column table for title and date
                    title_para = Paragraph(f"<b>{_safe(title)}</b>", body_style)
                    date_para = Paragraph(f"<b>{_safe(date_str)}</b>", body_style)
                    
                    date_col_width = 2.0 * 72
                    title_col_width = USABLE_WIDTH - date_col_width
                    
                    title_table = Table(
                        [[title_para, date_para]],
                        colWidths=[title_col_width, date_col_width],
                        hAlign='LEFT'
                    )
                    title_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ]))
                    story.append(title_table)
                else:
                    story.append(Paragraph(f"<b>{_safe(title)}</b>", body_style))
            
            # Render bullets
            if "bullets" in entry and isinstance(entry["bullets"], list):
                for bullet_item in entry["bullets"]:
                    if isinstance(bullet_item, dict):
                        bullet_text = bullet_item.get("text", "")
                    else:
                        bullet_text = str(bullet_item)
                    
                    if bullet_text:
                        story.append(Paragraph(f"• {_safe(bullet_text)}", bullet_style))
            
            # Add spacing between entries
            if entry_idx + 1 < len(entries):
                story.append(Spacer(1, 0.8))

        story.append(Spacer(1, SECTION_BOTTOM_SPACE * 72))

    doc.build(story)


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
    from core.input_parser import parse_resume_with_mistral

    filepath = "samples/resume.txt"
    sections = parse_resume_with_mistral(filepath)
    
    if sections:
        generate_pdf(sections, "outputs/test_simple_pdf.pdf")
        print("PDF generated successfully!")
    else:
        print("Error parsing resume")
