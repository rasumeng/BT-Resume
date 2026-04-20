#!/usr/bin/env python3
"""
Comprehensive validation test for the resume PDF data flow fix.
Verifies that all the issues mentioned by the user are resolved.
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


def validate_fixes():
    """Validate that all the reported issues are fixed"""
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE VALIDATION TEST")
    logger.info("Resume PDF Data Flow Fix Verification")
    logger.info("=" * 80)
    
    # Test data covering all resume sections
    test_data = {
        "contact": {
            "name": "Robert Asumeng",
            "email": "robert@example.com",
            "phone": "(555) 123-4567",
            "location": "San Francisco, CA",
            "linkedin": "linkedin.com/in/robert",
            "github": "github.com/robert"
        },
        "summary": "Results-driven software engineer with 5+ years of experience.",
        "work_experience": [
            {
                "position": "Software Engineer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "start_date": "Jan 2021",
                "end_date": "Present",
                "bullets": [
                    "Led development of microservices architecture",
                    "Implemented CI/CD pipeline",
                    "Mentored 3 junior developers"
                ]
            }
        ],
        "projects": [
            {
                "name": "Resume AI System",
                "date": "Jan 2024 – Present",
                "technologies": "Python, Flask, ReportLab",
                "bullets": [
                    "Built full-stack resume optimization platform",
                    "Implemented LLM-based parsing features"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "State University",
                "date": "May 2019"
            }
        ],
        "leadership": [
            {
                "title": "Tech Lead",
                "organization": "Developer Community",
                "date": "2022 – Present",
                "bullets": [
                    "Organized monthly meetups for 100+ engineers"
                ]
            }
        ],
        "skills": [
            {
                "category": "Programming Languages",
                "items": ["Python", "JavaScript"]
            }
        ]
    }
    
    # Import required modules
    logger.info("\n📦 Importing modules...")
    try:
        from core.resume_model import ResumData
        from core.pdf_generator import generate_pdf
        logger.info("✓ Imports successful")
    except Exception as e:
        logger.error(f"✗ Import failed: {e}")
        return False
    
    # Issue #1: Name field should not be "Resume"
    logger.info("\n" + "=" * 80)
    logger.info("ISSUE #1: Name Field")
    logger.info("=" * 80)
    logger.info("Problem: PDF shows 'Resume' instead of actual name")
    
    try:
        resume_data = ResumData.from_llm_json(test_data)
        
        if resume_data.contact.name == "Resume":
            logger.error("✗ FAIL: Name is still 'Resume'")
            return False
        elif resume_data.contact.name == "Robert Asumeng":
            logger.info(f"✓ PASS: Name correctly extracted: {resume_data.contact.name}")
        elif resume_data.contact.name == "":
            logger.error("✗ FAIL: Name is empty (not extracted)")
            return False
        else:
            logger.error(f"✗ FAIL: Unexpected name: {resume_data.contact.name}")
            return False
    except Exception as e:
        logger.error(f"✗ FAIL: Exception during parsing: {e}")
        return False
    
    # Issue #2: Work Experience should be present
    logger.info("\n" + "=" * 80)
    logger.info("ISSUE #2: Work Experience")
    logger.info("=" * 80)
    logger.info("Problem: Work experience completely missing from PDF")
    
    if len(resume_data.work_experience) == 0:
        logger.error("✗ FAIL: No work experience entries found")
        return False
    
    job = resume_data.work_experience[0]
    logger.info(f"✓ PASS: Found {len(resume_data.work_experience)} work experience entry(ies)")
    logger.info(f"  - Position: {job.position}")
    logger.info(f"  - Company: {job.company}")
    logger.info(f"  - Bullets: {len(job.bullets)} items")
    
    if len(job.bullets) == 0:
        logger.error("✗ FAIL: Work experience has no bullets")
        return False
    
    # Issue #3: Projects should show formatted content, not raw JSON
    logger.info("\n" + "=" * 80)
    logger.info("ISSUE #3: Projects Formatting")
    logger.info("=" * 80)
    logger.info("Problem: Projects show raw JSON instead of formatted content")
    
    if len(resume_data.projects) == 0:
        logger.error("✗ FAIL: No projects found")
        return False
    
    project = resume_data.projects[0]
    logger.info(f"✓ PASS: Found {len(resume_data.projects)} project(s)")
    logger.info(f"  - Name: {project.name}")
    logger.info(f"  - Technologies: {project.technologies}")
    logger.info(f"  - Bullets: {len(project.bullets)} items")
    
    # Check that projects are Project objects, not raw JSON strings
    if isinstance(project.name, str) and len(project.name) > 0:
        logger.info("✓ PASS: Project name is properly formatted string")
    else:
        logger.error("✗ FAIL: Project name is not a proper string")
        return False
    
    if len(project.bullets) > 0:
        bullet_text = project.bullets[0].text
        if "{" in bullet_text or "json" in bullet_text.lower():
            logger.error(f"✗ FAIL: Project bullet contains JSON: {bullet_text}")
            return False
        logger.info(f"✓ PASS: Project bullets are formatted text (not JSON)")
    
    # Additional sections verification
    logger.info("\n" + "=" * 80)
    logger.info("ADDITIONAL SECTIONS")
    logger.info("=" * 80)
    
    logger.info(f"Education entries: {len(resume_data.education)}")
    if len(resume_data.education) > 0:
        logger.info(f"  - First: {resume_data.education[0].degree} from {resume_data.education[0].school}")
    
    logger.info(f"Leadership entries: {len(resume_data.leadership)}")
    if len(resume_data.leadership) > 0:
        logger.info(f"  - First: {resume_data.leadership[0].title}")
    
    logger.info(f"Skill categories: {len(resume_data.skills)}")
    if len(resume_data.skills) > 0:
        logger.info(f"  - First: {resume_data.skills[0].category} ({len(resume_data.skills[0].items)} items)")
    
    # Validate the complete resume
    logger.info("\n" + "=" * 80)
    logger.info("FINAL VALIDATION")
    logger.info("=" * 80)
    
    is_valid, errors = resume_data.validate()
    
    if is_valid:
        logger.info("✓ PASS: Resume data validation successful")
    else:
        logger.error("✗ FAIL: Resume validation errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    # Test PDF generation
    logger.info("\n📄 Generating PDF to verify all sections render...")
    
    try:
        output_path = Path(__file__).parent / "outputs" / "validation_test_resume.pdf"
        output_path.parent.mkdir(exist_ok=True)
        
        success = generate_pdf(resume_data, str(output_path))
        
        if success and output_path.exists():
            logger.info(f"✓ PASS: PDF generated successfully")
            logger.info(f"  - File: {output_path}")
            logger.info(f"  - Size: {output_path.stat().st_size} bytes")
        else:
            logger.error("✗ FAIL: PDF generation failed")
            return False
    except Exception as e:
        logger.error(f"✗ FAIL: PDF generation error: {e}")
        return False
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ ALL VALIDATIONS PASSED")
    logger.info("=" * 80)
    logger.info("\nSummary of Fixed Issues:")
    logger.info("  ✅ Issue #1: Name field correctly shows 'Robert Asumeng' (not 'Resume')")
    logger.info(f"  ✅ Issue #2: Work experience present with {len(job.bullets)} properly formatted bullets")
    logger.info(f"  ✅ Issue #3: Projects show formatted content (not raw JSON)")
    logger.info(f"\nAdditional Data:")
    logger.info(f"  - Education: {len(resume_data.education)} entry(ies)")
    logger.info(f"  - Leadership: {len(resume_data.leadership)} entry(ies)")
    logger.info(f"  - Skills: {len(resume_data.skills)} category(ies)")
    logger.info(f"\nPDF Output: {output_path}")
    
    return True


if __name__ == "__main__":
    success = validate_fixes()
    sys.exit(0 if success else 1)
