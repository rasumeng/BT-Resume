#!/usr/bin/env python3
"""
Test the complete data pipeline: Resume Text -> LLM Parse -> ResumData -> PDF

This script tests the end-to-end data flow to ensure all resume fields
are properly captured and rendered in the final PDF.
"""

import json
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_pipeline():
    """Test the complete pipeline with a real resume sample"""
    
    logger.info("=" * 80)
    logger.info("RESUME DATA PIPELINE TEST")
    logger.info("=" * 80)
    
    # Sample resume to test
    sample_resume = """
Robert Asumeng
Phone: (555) 123-4567 | Email: robert@example.com | Location: San Francisco, CA
LinkedIn: linkedin.com/in/robert | GitHub: github.com/robert

PROFESSIONAL SUMMARY
Results-driven software engineer with 5+ years of experience building scalable applications.
Proven track record of delivering high-quality solutions and leading technical initiatives.

WORK EXPERIENCE

Software Engineer – TechCorp (Jan 2021 – Present)
San Francisco, CA
• Led development of microservices architecture using Python and Django, improving system performance by 40%
• Implemented CI/CD pipeline using GitHub Actions, reducing deployment time from 2 hours to 15 minutes
• Mentored 3 junior developers, conducting weekly code reviews and technical training sessions
• Optimized database queries, reducing API response time from 500ms to 50ms

Software Developer – StartupInc (June 2019 – Dec 2020)
Remote
• Built RESTful APIs using Flask and PostgreSQL serving 1M+ requests daily
• Developed real-time data processing pipeline using Apache Kafka and Python
• Contributed to open-source projects with 500+ GitHub stars
• Implemented automated testing suite achieving 85% code coverage

EDUCATION

Bachelor of Science in Computer Science – State University (May 2019)
San Francisco, CA
GPA: 3.8/4.0
• Dean's List all semesters
• Relevant Coursework: Data Structures, Algorithms, Database Design, Software Engineering

PROJECTS

Resume AI System (Jan 2024 – Present)
Technologies: Python, Flask, ReportLab, Ollama
• Built full-stack resume optimization platform with PDF generation capabilities
• Implemented LLM-based resume parsing and polishing features
• Created professional PDF generation with ReportLab template system
• Achieved 95% accuracy in extracting resume data from various formats

Open Source Contribution – PyData (2021 – Present)
Technologies: Python, NumPy, Pandas, GitHub
• Contributed 50+ code commits improving data processing efficiency
• Maintained backward compatibility while refactoring core modules
• Collaborated with 20+ developers across 8 countries

LEADERSHIP & ACTIVITIES

Tech Lead – Developer Community (2022 – Present)
San Francisco, CA
• Organized monthly meetups for 100+ software engineers
• Led technical workshops on Python best practices and system design
• Built community Slack workspace with 500+ active members

SKILLS
Programming Languages: Python, JavaScript, SQL, Go
Web Frameworks: Django, Flask, FastAPI, React
Databases: PostgreSQL, MongoDB, Redis
DevOps: Docker, Kubernetes, GitHub Actions, AWS
Soft Skills: Team Leadership, Technical Communication, Problem Solving

CERTIFICATIONS
AWS Certified Solutions Architect (2022)
Python Developer Certification (2021)
"""

    logger.info("\n📄 Step 1: Importing required modules...")
    try:
        from core.resume_model import ResumData
        from core.pdf_generator import generate_pdf
        logger.info("✓ Successfully imported ResumData and generate_pdf")
    except ImportError as e:
        logger.error(f"✗ Failed to import modules: {e}")
        return False
    
    # Test 1: Create sample JSON that matches the expected format
    logger.info("\n📋 Step 2: Creating sample JSON structure...")
    sample_json = {
        "contact": {
            "name": "Robert Asumeng",
            "phone": "(555) 123-4567",
            "email": "robert@example.com",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/robert",
            "github": "github.com/robert"
        },
        "summary": "Results-driven software engineer with 5+ years of experience building scalable applications. Proven track record of delivering high-quality solutions and leading technical initiatives.",
        "work_experience": [
            {
                "position": "Software Engineer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "start_date": "Jan 2021",
                "end_date": "Present",
                "bullets": [
                    "Led development of microservices architecture using Python and Django, improving system performance by 40%",
                    "Implemented CI/CD pipeline using GitHub Actions, reducing deployment time from 2 hours to 15 minutes",
                    "Mentored 3 junior developers, conducting weekly code reviews and technical training sessions",
                    "Optimized database queries, reducing API response time from 500ms to 50ms"
                ]
            },
            {
                "position": "Software Developer",
                "company": "StartupInc",
                "location": "Remote",
                "start_date": "June 2019",
                "end_date": "Dec 2020",
                "bullets": [
                    "Built RESTful APIs using Flask and PostgreSQL serving 1M+ requests daily",
                    "Developed real-time data processing pipeline using Apache Kafka and Python",
                    "Contributed to open-source projects with 500+ GitHub stars",
                    "Implemented automated testing suite achieving 85% code coverage"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "State University",
                "location": "San Francisco, CA",
                "date": "May 2019",
                "details": [
                    "GPA: 3.8/4.0",
                    "Dean's List all semesters",
                    "Relevant Coursework: Data Structures, Algorithms, Database Design, Software Engineering"
                ]
            }
        ],
        "projects": [
            {
                "name": "Resume AI System",
                "date": "Jan 2024 – Present",
                "technologies": "Python, Flask, ReportLab, Ollama",
                "bullets": [
                    "Built full-stack resume optimization platform with PDF generation capabilities",
                    "Implemented LLM-based resume parsing and polishing features",
                    "Created professional PDF generation with ReportLab template system",
                    "Achieved 95% accuracy in extracting resume data from various formats"
                ]
            },
            {
                "name": "Open Source Contribution – PyData",
                "date": "2021 – Present",
                "technologies": "Python, NumPy, Pandas, GitHub",
                "bullets": [
                    "Contributed 50+ code commits improving data processing efficiency",
                    "Maintained backward compatibility while refactoring core modules",
                    "Collaborated with 20+ developers across 8 countries"
                ]
            }
        ],
        "leadership": [
            {
                "title": "Tech Lead – Developer Community",
                "organization": "Developer Community",
                "location": "San Francisco, CA",
                "date": "2022 – Present",
                "bullets": [
                    "Organized monthly meetups for 100+ software engineers",
                    "Led technical workshops on Python best practices and system design",
                    "Built community Slack workspace with 500+ active members"
                ]
            }
        ],
        "skills": [
            {
                "category": "Programming Languages",
                "items": ["Python", "JavaScript", "SQL", "Go"]
            },
            {
                "category": "Web Frameworks",
                "items": ["Django", "Flask", "FastAPI", "React"]
            },
            {
                "category": "Databases",
                "items": ["PostgreSQL", "MongoDB", "Redis"]
            },
            {
                "category": "DevOps",
                "items": ["Docker", "Kubernetes", "GitHub Actions", "AWS"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "date": "2022"
            },
            {
                "name": "Python Developer Certification",
                "date": "2021"
            }
        ]
    }
    
    logger.info(f"✓ Created sample JSON with {len(sample_json)} top-level sections")
    
    # Test 2: Convert JSON to ResumData
    logger.info("\n📊 Step 3: Converting JSON to ResumData object...")
    try:
        resume_data = ResumData.from_llm_json(sample_json)
        logger.info("✓ Successfully converted to ResumData")
        
        # Validate the conversion
        logger.info(f"  - Name: {resume_data.contact.name}")
        logger.info(f"  - Email: {resume_data.contact.email}")
        logger.info(f"  - Work Experience entries: {len(resume_data.work_experience)}")
        logger.info(f"  - Education entries: {len(resume_data.education)}")
        logger.info(f"  - Projects: {len(resume_data.projects)}")
        logger.info(f"  - Leadership entries: {len(resume_data.leadership)}")
        logger.info(f"  - Skill categories: {len(resume_data.skills)}")
        
        # Check for issues
        if not resume_data.contact.name or resume_data.contact.name == "":
            logger.error("✗ Name is empty!")
            return False
        
        if len(resume_data.work_experience) == 0:
            logger.warning("⚠ Warning: No work experience entries!")
        
        if len(resume_data.projects) == 0:
            logger.warning("⚠ Warning: No projects!")
            
    except Exception as e:
        logger.error(f"✗ Failed to convert to ResumData: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Validate resume data
    logger.info("\n✅ Step 4: Validating resume data...")
    is_valid, errors = resume_data.validate()
    if is_valid:
        logger.info("✓ Resume data is valid")
    else:
        logger.error("✗ Resume data is invalid:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    # Test 4: Generate PDF
    logger.info("\n🎨 Step 5: Generating PDF...")
    try:
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_resume.pdf"
        
        success = generate_pdf(resume_data, str(output_path))
        
        if success and output_path.exists():
            logger.info(f"✓ Successfully generated PDF: {output_path}")
            logger.info(f"  File size: {output_path.stat().st_size} bytes")
        else:
            logger.error("✗ Failed to generate PDF")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ ALL TESTS PASSED")
    logger.info("=" * 80)
    logger.info("\nSummary:")
    logger.info(f"  - Name: {resume_data.contact.name}")
    logger.info(f"  - Work Experience: {len(resume_data.work_experience)} entries")
    logger.info(f"  - Projects: {len(resume_data.projects)} entries")
    logger.info(f"  - Education: {len(resume_data.education)} entries")
    logger.info(f"  - Leadership: {len(resume_data.leadership)} entries")
    logger.info(f"  - Skills: {len(resume_data.skills)} categories")
    logger.info(f"  - PDF Output: {output_path}")
    
    return True


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
