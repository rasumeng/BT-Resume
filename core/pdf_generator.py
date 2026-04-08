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

PREFERRED_SECTION_ORDER = [
    "EDUCATION",
    "WORK EXPERIENCE",
    "PROJECTS",
    "SKILLS",
    "LEADERSHIP",
]


def _extract_date_from_title(line: str) -> tuple:
    """
    Extract date range from a title line.
    Returns (title_without_date, date_string) or (line, None) if no date found.
    
    Examples:
    - "AI Trainer – Handshake  Dec 2025 – Present" -> ("AI Trainer – Handshake", "Dec 2025 – Present")
    - "Data Systems Engineer – FAPEMPA LLC  Feb 2023 – Dec 2024" -> ("Data Systems Engineer – FAPEMPA LLC", "Feb 2023 – Dec 2024")
    """
    # Pattern: Month Year – Month Year OR Month Year – Present
    date_pattern = r'\b([A-Z][a-z]{2}\s+\d{4})\s+[–-]\s+(Present|[A-Z][a-z]{2}\s+\d{4})\s*$'
    match = re.search(date_pattern, line)
    
    if match:
        date_str = match.group(0).strip()
        title = line[:match.start()].strip()
        return (title, date_str)
    
    return (line, None)


def generate_pdf(sections: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=PAGE_LEFT_MARGIN * 72,
        rightMargin=PAGE_RIGHT_MARGIN * 72,
        topMargin=PAGE_TOP_MARGIN * 72,
        bottomMargin=PAGE_BOTTOM_MARGIN * 72,
    )

    header_style = ParagraphStyle(
        "section_header",
        fontName="Helvetica-Bold",
        fontSize=SECTION_HEADER_FONT_SIZE,
        leading=SECTION_HEADER_FONT_SIZE + 1,
        spaceBefore=0,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    title_style = ParagraphStyle(
        "entry_title",
        fontName="Helvetica-Bold",
        fontSize=SECTION_BODY_FONT_SIZE,
        leading=SECTION_LEADING,
        spaceAfter=0,
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
        # Build structured contact line from extracted info
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
            # Extract name from header
            header_block = sections.get("_HEADER", "")
            if header_block:
                header_lines = [line.strip() for line in header_block.split("\n") if line.strip()]
                if header_lines:
                    # Look for a simple name in the header
                    extracted_name = _extract_name_from_header(header_lines[0])
                    
                    if extracted_name:
                        # Render the name prominently on its own line
                        story.append(Paragraph(f"<b>{_safe(extracted_name)}</b>", top_name_style))
                        # Add a small line break spacer between name and contact info
                        story.append(Spacer(1, 6))
                        # Render contact info
                        story.append(Paragraph(_safe(" | ".join(contact_line_parts)), top_info_style))
                        story.append(Spacer(1, HEADER_BOTTOM_SPACE * 72))
                    else:
                        # No name found, just render contact info
                        story.append(Paragraph(_safe(" | ".join(contact_line_parts)), top_info_style))
                        story.append(Spacer(1, HEADER_BOTTOM_SPACE * 72))
                else:
                    # No header lines, just render contact info
                    story.append(Paragraph(_safe(" | ".join(contact_line_parts)), top_info_style))
                    story.append(Spacer(1, HEADER_BOTTOM_SPACE * 72))
            else:
                # No header found, just render contact info
                story.append(Paragraph(_safe(" | ".join(contact_line_parts)), top_info_style))
                story.append(Spacer(1, HEADER_BOTTOM_SPACE * 72))
    else:
        # Fallback to original header rendering if contact extraction failed
        header_block = sections.get("_HEADER", "")
        if header_block:
            header_lines = [line.strip() for line in header_block.split("\n") if line.strip()]
            if header_lines:
                # Look for the first line that's just a simple name (2-3 capitalized words, no special chars)
                name_idx = None
                extracted_name = None
                
                for i, line in enumerate(header_lines):
                    if _is_simple_name(line):
                        name_idx = i
                        break
                
                # If no simple name found across lines, try to extract from first line
                if name_idx is None and header_lines:
                    first_line = header_lines[0]
                    # Try to extract name from beginning of line before email or pipe
                    extracted_name = _extract_name_from_header(first_line)

                if name_idx is not None:
                    # Render the name prominently on its own line
                    story.append(Paragraph(f"<b>{_safe(header_lines[name_idx])}</b>", top_name_style))
                    # Add a small line break spacer between name and contact info
                    story.append(Spacer(1, 6))
                    # Then render contact info below
                    for i, line in enumerate(header_lines):
                        if i != name_idx:
                            story.append(Paragraph(_safe(line), top_info_style))
                elif extracted_name:
                    # Render extracted name prominently
                    story.append(Paragraph(f"<b>{_safe(extracted_name)}</b>", top_name_style))
                    # Add a small line break spacer between name and contact info
                    story.append(Spacer(1, 6))
                    # Render the remaining contact info (skip first line since we extracted name from it)
                    for i, line in enumerate(header_lines):
                        if i > 0:  # Skip the first line (where we extracted the name from)
                            story.append(Paragraph(_safe(line), top_info_style))
                else:
                    # No simple name found; render all lines as contact info
                    for line in header_lines:
                        story.append(Paragraph(_safe(line), top_info_style))
                story.append(Spacer(1, HEADER_BOTTOM_SPACE * 72))

    ordered_sections = []
    for section_name in PREFERRED_SECTION_ORDER:
        if section_name in sections and section_name != "_HEADER":
            ordered_sections.append((section_name, sections[section_name]))

    for section_name, content in sections.items():
        if section_name == "_HEADER" or section_name == "_CONTACT" or section_name in PREFERRED_SECTION_ORDER:
            continue
        ordered_sections.append((section_name, content))

    for section, content in ordered_sections:
        if section == "_HEADER":
            continue
        section_name = _safe(section).upper()
        lines = [line.strip() for line in (content or "").split("\n")]
        lines = [line for line in lines if line]
        if not lines:
            continue

        story.append(Spacer(1, SECTION_TOP_SPACE * 72))
        story.append(Paragraph(section_name, header_style))
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

        for idx, line in enumerate(lines):
            clean_line = _normalize_render_line(line)
            safe_line = _safe(clean_line)
            is_bullet = bool(re.match("^[\\\"'""''\\s]*[-*•●]+\\s*", clean_line))

            if is_bullet:
                bullet_text = re.sub("^[\\\"'""''\\s]*[-*•●]+\\s*", "", clean_line).strip()
                bullet_text = _strip_wrapping_quotes(bullet_text)
                if bullet_text:
                    story.append(Paragraph(f"• {_safe(bullet_text)}", bullet_style))
            else:
                next_is_bullet = False
                if idx + 1 < len(lines):
                    next_line = _normalize_render_line(lines[idx + 1])
                    next_is_bullet = bool(re.match("^[\\\"'""''\\s]*[-*•●]+\\s*", next_line))

                if next_is_bullet:
                    # Check if this title line has a date that should be right-aligned
                    title_without_date, date_str = _extract_date_from_title(clean_line)
                    
                    if date_str:
                        # Use a two-column table that properly spans full width
                        # Both columns are Paragraph objects to maintain consistent styling
                        title_para = Paragraph(f"<b>{_safe(title_without_date)}</b>", body_style)
                        date_para = Paragraph(f"<b>{_safe(date_str)}</b>", body_style)
                        
                        # Create table with proper width allocation
                        date_col_width = 2.0 * 72  # 144 points for date column
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
                        story.append(Paragraph(safe_line, title_style))
                else:
                    story.append(Paragraph(safe_line, body_style))

            # Preserve readable breaks between entries.
            if idx + 1 < len(lines) and not is_bullet and not lines[idx + 1].startswith("-"):
                story.append(Spacer(1, 0.8))

        story.append(Spacer(1, SECTION_BOTTOM_SPACE * 72))

    doc.build(story)


def _safe(value: str) -> str:
    return html.escape((value or "").strip())


def _strip_wrapping_quotes(value: str) -> str:
    stripped = (value or "").strip()
    quote_pairs = [
        ('"', '"'),
        ("'", "'"),
        ("“", "”"),
        ("‘", "’"),
    ]
    changed = True
    while changed and len(stripped) >= 2:
        changed = False
        for left, right in quote_pairs:
            if stripped.startswith(left) and stripped.endswith(right):
                stripped = stripped[1:-1].strip()
                changed = True
    return stripped


def _normalize_render_line(line: str) -> str:
    stripped = (line or "").strip()
    stripped = _strip_wrapping_quotes(stripped)
    return re.sub(r"\s+", " ", stripped).strip()


def _looks_like_name(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if "@" in stripped or "http" in stripped.lower() or "www." in stripped.lower():
        return False
    if any(ch.isdigit() for ch in stripped):
        return False
    words = [w for w in stripped.split() if w]
    if not (2 <= len(words) <= 5):
        return False
    return all(any(c.isalpha() for c in w) for w in words)


def _is_simple_name(line: str) -> bool:
    """Check if a line is a simple name: 2-3 capitalized words with only alphabetic characters.
    
    Examples that match:
    - "Robert Asumeng"
    - "John Smith"
    - "Mary Jane Watson"
    
    Examples that don't match:
    - "asumengrobert787@gmail.com" (contains @, numbers)
    - "SWE Engineer | Senior" (contains special char)
    - "A" (too short)
    - "robert asumeng" (not capitalized)
    """
    stripped = line.strip()
    if not stripped:
        return False
    
    # No special characters or numbers allowed
    if not all(c.isalpha() or c.isspace() for c in stripped):
        return False
    
    words = stripped.split()
    if not (2 <= len(words) <= 3):
        return False
    
    # Each word should be capitalized (first letter uppercase)
    return all(word and word[0].isupper() for word in words)


def _extract_name_from_header(line: str) -> str:
    """Extract name from a header line that may contain name, email, and other contact info.
    
    Examples:
    - "Robert Asumeng asumengrobert787@gmail.com | 469-594-2623" -> "Robert Asumeng"
    - "John Smith john@example.com | LinkedIn: ..." -> "John Smith"
    """
    # Split by common delimiters to get the first part
    first_part = line.split("|")[0].split("@")[0].strip()
    
    # Extract words that look like a name (alphabetic, capitalized)
    words = first_part.split()
    name_words = []
    
    for word in words:
        # Stop if we hit something that doesn't look like a name word
        if not all(c.isalpha() or c.isspace() for c in word):
            break
        name_words.append(word)
    
    # If we got 2-3 name-like words that are capitalized, that's likely the name
    extracted = " ".join(name_words)
    if 2 <= len(name_words) <= 3 and _is_simple_name(extracted):
        return extracted
    
    return ""


if __name__ == "__main__":
    from core.input_parser import load_text, parse_section, load_pdf
    from core.output_builder import build_resume

    text = load_pdf("samples/resume.pdf")
    sections = parse_section(text)
    # Skip polishing for faster testing - use raw parsed sections
    generate_pdf(sections, "outputs/resume_output.pdf")
    print("PDF generated!")