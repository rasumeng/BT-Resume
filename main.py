import argparse
from core.input_parser import load_text, load_pdf, parse_section
from core.output_builder import build_resume
from core.pdf_generator import generate_pdf



def main():
    parser = argparse.ArgumentParser(description="ResumeBuilder")
    parser.add_argument("--resume", required=True)
    parser.add_argument("--job", default=None)
    parser.add_argument("--output", default="outputs/resume_output.pdf")
    parser.add_argument("--add-experience", action="store_true")
    args = parser.parse_args()

    resume_path = args.resume
    output_path = args.output
    job_path = args.job
    experience = args.add_experience


    print("Loading resume...")
    if resume_path.endswith(".pdf"):
        text = load_pdf(resume_path)
    else:
        text = load_text(resume_path)

    if job_path:
        print("Loading job description...")
        job_description = load_text(job_path)  # only load if provided
    else:
        job_description = None

    print("Parsing resume sections...")
    sections = parse_section(text)

    if experience:
        from core.prompts import experience_updater_prompt
        from core.llm_client import ask_llm
        from core.output_builder import clean_bullets
        
        user_input = input("Describe your experience: ")
        section = input("Which section? (WORK EXPERIENCE / PROJECTS / LEADERSHIP): ").upper()
        title = input("What's the title for this experience? (e.g. 'Software Engineer Intern – Company'): ")

        
        prompt = experience_updater_prompt(user_input)
        new_bullets = ask_llm(prompt)
        new_bullets = clean_bullets(new_bullets)
        
        # Append to the correct section
        if section in sections:
            sections[section] += f"\n{title}\n{new_bullets}\n"
        else:
            sections[section] = new_bullets

    print("Building structured resume...")
    resume_data = build_resume(sections, job_description)

    print("Generating PDF...")
    generate_pdf(resume_data, output_path)

    print("PDF Generated!")

if __name__ == "__main__":
    main()