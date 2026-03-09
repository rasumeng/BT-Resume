import argparse
from input_parser import load_resume, parse_section
from output_builder import build_resume
from pdf_generator import generate_pdf



def main():
    parser = argparse.ArgumentParser(description="ResumeBuilder")
    parser.add_argument("--resume", required=True)
    parser.add_argument("--output", default="outputs/resume_output.pdf")
    args = parser.parse_args()

    resume_path = args.resume
    output_path = args.output

    print("Loading resume...")
    text = load_resume(resume_path)

    print("Parsing sections...")
    sections = parse_section(text)

    print("Building structured resume...")
    resume_data = build_resume(sections)

    print("Generating PDF...")
    generate_pdf(resume_data, output_path)

    print("PDF Generated!")
if __name__ == "__main__":
    main()