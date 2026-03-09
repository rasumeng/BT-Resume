from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

def generate_pdf(sections: dict, output_path: str):
    # Create the document
    doc  = SimpleDocTemplate(output_path, pagesize=letter)
    normal_style = ParagraphStyle(
        "custom",
        fontName="Helvetica",
        fontSize=10,
        leading=10,  # line spacing
        spaceAfter=2
    )
    header_style = ParagraphStyle(
        "custom_header",
        fontName="Helvetica-Bold",  # bold looks better for headers
        fontSize=12,
        spaceBefore=4,
        spaceAfter=4,
    )

    styles =getSampleStyleSheet()
    story = []

    for section, content in sections.items():
        content = content.replace("\n", "<br/>")
        story.append(Paragraph(section, header_style))
        story.append(Paragraph(content, normal_style))
        story.append(Spacer(1, 0.2 * inch))

        
    # Build and save
    doc.build(story)


if __name__ == "__main__":
    from input_parser import load_resume, parse_section
    from output_builder import build_resume

    text = load_resume("samples/resume.txt")
    sections = parse_section(text)
    improved = build_resume(sections)
    generate_pdf(improved, "outputs/resume_output.pdf")
    print("PDF generated!")