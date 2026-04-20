#!/usr/bin/env python
"""
Example: Using the new Alteration Service with Structured Resume Data

Demonstrates:
1. Creating a structured resume from the template
2. Polishing it using the LLM
3. Saving with full version tracking
4. Retrieving history and statistics
"""

import json
from pathlib import Path
from backend.services.file_service import FileService
from backend.services.llm_service import LLMService

# ============================================================================
# EXAMPLE 1: Complete Alteration Workflow
# ============================================================================

def example_polish_with_versioning():
    """
    Complete workflow: Polish resume with versioning and metadata tracking.
    """
    print("="*70)
    print("EXAMPLE 1: Polish Resume with Versioning")
    print("="*70)
    
    # Step 1: Original resume text
    original_resume = """
ROBERT ASUMENG
asumengrobert787@gmail.com | (469) 594-2623
linkedin.com/in/robertasumeng | github.com/rasumeng

SUMMARY
Experienced software engineer with expertise in AI/ML, data systems, and full-stack development.

EXPERIENCE
AI Trainer - Handshake AI Fellowship
Dec 2025 - Present
- Created and tested AI prompts for model refinement
- Reviewed AI-generated outputs for consistency
- Improved model performance through iterative refinement

Data System Engineer - FAPEMPA LLC
Feb 2023 - Dec 2024
- Built ETL pipelines processing financial data
- Automated reporting tools with Python
- Developed SQL queries for multi-site reconciliation

EDUCATION
Bachelor of Science in Computer Science
University of Texas at Arlington, May 2027
GPA: 3.8/4.0

SKILLS
Python, C/C++, SQL, JavaScript, Flask, React, Git
Machine Learning, Data Analysis, ETL, System Design
"""

    print("Original Resume:")
    print(original_resume)
    print()
    
    # Step 2: Polish the resume
    print("📝 Polishing resume with LLM...")
    polish_result = LLMService.polish_resume(original_resume, intensity='medium')
    
    if not polish_result.get('success'):
        print(f"❌ Polish failed: {polish_result.get('error')}")
        return
    
    polished_text = polish_result['polished_resume']
    parsed_json = polish_result.get('parsed_json')  # May be included by LLM service
    print(f"✓ Polished text length: {len(polished_text)} characters")
    print()
    
    # Step 3: Save with versioning
    print("💾 Saving with full version tracking...")
    save_result = FileService.save_altered_resume(
        original_filename="resume.pdf",
        altered_text=polished_text,
        parsed_json=parsed_json,  # Optional - avoids re-parsing
        alteration_type='polish',
        intensity='medium'
    )
    
    if save_result['success']:
        print("✓ Alteration saved successfully!")
        print(f"  - Text file: {save_result['text_file']}")
        print(f"  - PDF file: {save_result['pdf_file']}")
        print(f"  - Alteration ID: {save_result['alteration_id']}")
        print(f"  - Status: {save_result['status']}")
        print(f"  - Total versions: {save_result['history_count']}")
    else:
        print(f"❌ Save failed: {save_result['error']}")
        return
    
    print()
    return save_result


# ============================================================================
# EXAMPLE 2: Structured Resume Data
# ============================================================================

def example_structured_resume_data():
    """
    Working with structured resume data (JSON template format).
    """
    print("="*70)
    print("EXAMPLE 2: Using Structured Resume Template")
    print("="*70)
    
    structured_resume = {
        "resume": {
            "header": {
                "name": "Robert Asumeng",
                "contact": {
                    "email": "asumengrobert787@gmail.com",
                    "phone": "469-594-2623",
                    "linkedin": "www.linkedin.com/in/robertasumeng/",
                    "github": "github.com/rasumeng"
                }
            },
            "technical_skills": {
                "programming_languages": ["Python", "C/C++", "SQL", "Java", "HTML/CSS", "C#"],
                "ai_ml": ["LLM Integration", "Prompt Engineering", "ML Pipelines", "Model Evaluation"],
                "data": ["Pandas", "NumPy", "Scikit-learn", "ETL", "Data Cleaning"],
                "tools": ["Git", "GitHub", "Linux", "VS Code", "Jupyter"],
                "soft_skills": ["Analytical Thinking", "Communication", "Leadership", "Adaptability"]
            },
            "work_experience": [
                {
                    "position": "AI Trainer",
                    "company": "Handshake AI Fellowship",
                    "start_date": "Dec 2025",
                    "end_date": "Present",
                    "duration_months": 4,
                    "key_responsibilities": [
                        {
                            "task": "Created and tested AI prompts",
                            "scale": "50+",
                            "outcome": "Improved model outputs",
                            "metric": "Average QA rating of 2.72"
                        },
                        {
                            "task": "Reviewed AI-generated outputs",
                            "focus": "Logical consistency",
                            "metric": "Identified errors in 19% of submissions"
                        }
                    ]
                },
                {
                    "position": "Data System Engineer",
                    "company": "FAPEMPA LLC",
                    "start_date": "Feb 2023",
                    "end_date": "Dec 2024",
                    "duration_months": 23,
                    "key_responsibilities": [
                        {
                            "task": "Built scalable ETL pipelines",
                            "scope": "Financial data across 10+ sites",
                            "metric": "40% improvement in throughput"
                        },
                        {
                            "task": "Automated financial reporting tools",
                            "technology": "Python",
                            "metrics": ["70% reduction in processing time", "40% increase in reliability"]
                        }
                    ]
                }
            ],
            "education": [
                {
                    "institution": "University of Texas at Arlington",
                    "degree": "Bachelor of Science in Computer Science",
                    "start_date": "Aug 2023",
                    "end_date": "May 2027",
                    "gpa": "3.8/4.0",
                    "status": "current_student"
                }
            ],
            "projects": [
                {
                    "name": "Beyond The Resume (BTR)",
                    "start_date": "Mar 2026",
                    "end_date": "Present",
                    "status": "ongoing",
                    "technologies": ["Python", "Ollama LLMs", "Mistral 7B", "LLaMA 3 8B"],
                    "description": "Local AI resume optimization pipeline",
                    "key_features": [
                        {
                            "feature": "Smart model routing",
                            "purpose": "Balance speed and quality across NLP tasks"
                        },
                        {
                            "feature": "Modular prompt engineering",
                            "capability": "Iterative refinement with hallucination prevention"
                        }
                    ]
                }
            ],
            "certifications": [
                {
                    "name": "Google Data Analytics Professional Certificate",
                    "date_completed": "Apr 2026"
                }
            ]
        }
    }
    
    print("Structured Resume Created with:")
    print(f"  - Name: {structured_resume['resume']['header']['name']}")
    print(f"  - Contact fields: {list(structured_resume['resume']['header']['contact'].keys())}")
    print(f"  - Skill categories: {list(structured_resume['resume']['technical_skills'].keys())}")
    print(f"  - Work experiences: {len(structured_resume['resume']['work_experience'])}")
    print(f"  - Projects: {len(structured_resume['resume']['projects'])}")
    print(f"  - Certifications: {len(structured_resume['resume']['certifications'])}")
    print()
    
    # Use for LLM prompting
    structured_json_str = json.dumps(structured_resume, indent=2)
    print(f"Structured JSON length: {len(structured_json_str)} characters")
    print()
    
    return structured_resume


# ============================================================================
# EXAMPLE 3: Tailor Resume to Job Description
# ============================================================================

def example_tailor_resume():
    """
    Tailor resume to a specific job description with versioning.
    """
    print("="*70)
    print("EXAMPLE 3: Tailor Resume to Job Description")
    print("="*70)
    
    resume_text = """
ROBERT ASUMENG
asumengrobert787@gmail.com | (469) 594-2623

EXPERIENCE
AI Trainer - Handshake AI Fellowship (Dec 2025 - Present)
- Created and tested AI prompts for model refinement
- Reviewed outputs for consistency and accuracy

Data System Engineer - FAPEMPA LLC (Feb 2023 - Dec 2024)
- Built ETL pipelines for financial data processing
- Automated reporting with Python and SQL
"""
    
    job_description = """
Senior ML Engineer - TechCorp AI
We're looking for an ML engineer with:
- 3+ years experience building machine learning systems
- Expert Python skills
- Experience with data pipelines and ETL
- Strong understanding of LLM systems
- Experience optimizing model outputs
- Leadership and mentoring experience
"""
    
    print("Tailoring resume to job description...")
    tailor_result = LLMService.tailor_resume(resume_text, job_description)
    
    if tailor_result['success']:
        tailored_text = tailor_result['tailored_resume']
        print(f"✓ Resume tailored successfully!")
        print(f"  - Original length: {len(resume_text)} characters")
        print(f"  - Tailored length: {len(tailored_text)} characters")
        print()
        
        # Save tailored version
        print("💾 Saving tailored resume with version tracking...")
        save_result = FileService.save_altered_resume(
            original_filename="resume.pdf",
            altered_text=tailored_text,
            alteration_type='tailor',
            job_description="Senior ML Engineer - TechCorp AI"
        )
        
        if save_result['success']:
            print("✓ Tailored resume saved!")
            print(f"  - Alteration ID: {save_result['alteration_id']}")
            print(f"  - Total versions: {save_result['history_count']}")
        else:
            print(f"❌ Save failed: {save_result['error']}")
    else:
        print(f"❌ Tailor failed: {tailor_result['error']}")
    
    print()


# ============================================================================
# EXAMPLE 4: Retrieve Version History
# ============================================================================

def example_retrieve_history():
    """
    Retrieve and display complete version history for a resume.
    """
    print("="*70)
    print("EXAMPLE 4: Retrieve Version History")
    print("="*70)
    
    history = FileService.get_alteration_history("resume.pdf")
    
    if not history['success']:
        print(f"❌ Error: {history['error']}")
        return
    
    print(f"Resume: {history['filename']}")
    print(f"History created: {history['created']}")
    print(f"Total alterations: {history['total_alterations']}")
    print()
    
    print("Version Timeline:")
    for i, alt in enumerate(history['alterations'], 1):
        print(f"\n{i}. {alt['type'].upper()} (ID: {alt['id'][:8]}...)")
        print(f"   Timestamp: {alt['timestamp']}")
        print(f"   Status: {alt['status']}")
        if alt.get('intensity'):
            print(f"   Intensity: {alt['intensity']}")
        print(f"   Text file: {alt['text_file']}")
        print(f"   PDF file: {alt['pdf_file']}")
    
    print()


# ============================================================================
# EXAMPLE 5: Retrieve Statistics
# ============================================================================

def example_retrieve_stats():
    """
    Get and display alteration statistics.
    """
    print("="*70)
    print("EXAMPLE 5: Alteration Statistics")
    print("="*70)
    
    stats = FileService.get_alteration_stats("resume.pdf")
    
    if not stats['success']:
        print(f"❌ Error: {stats['error']}")
        return
    
    print(f"Total alterations: {stats['total_alterations']}")
    print(f"By type: {stats['by_type']}")
    
    if stats.get('latest_alteration'):
        latest = stats['latest_alteration']
        print(f"\nLatest alteration:")
        print(f"  Type: {latest['type']}")
        print(f"  Timestamp: {latest['timestamp']}")
        print(f"  Status: {latest['status']}")
    
    print()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔"+"="*68+"╗")
    print("║" + " "*15 + "RESUME ALTERATION SYSTEM - EXAMPLES" + " "*20 + "║")
    print("╚"+"="*68+"╝")
    print()
    
    # Uncomment examples to run
    
    # example_polish_with_versioning()
    # example_structured_resume_data()
    # example_tailor_resume()
    # example_retrieve_history()
    # example_retrieve_stats()
    
    print("To run examples, uncomment them in the if __name__ == '__main__' block")
    print()
    
    print("Examples available:")
    print("  1. example_polish_with_versioning()")
    print("  2. example_structured_resume_data()")
    print("  3. example_tailor_resume()")
    print("  4. example_retrieve_history()")
    print("  5. example_retrieve_stats()")
    print()
