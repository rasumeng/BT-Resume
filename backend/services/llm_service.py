"""
LLM Service - Handles all LLM calls for resume processing.
Wraps core.llm_client and provides clean interfaces for resume operations.
"""

import logging
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from llm_client import ask_llm, parse_resume_to_pdf_format
    LLM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LLM client not available: {e}")
    LLM_AVAILABLE = False

from config import MODELS

class LLMService:
    """Service for LLM-powered resume operations."""
    
    @staticmethod
    def polish_bullets(bullets: List[str], intensity: str = "medium") -> Dict:
        """
        Polish resume bullets to be stronger and ATS-optimized.
        
        Args:
            bullets: List of bullet points to polish
            intensity: 'light', 'medium', or 'heavy'
            
        Returns:
            Dict with polished bullets
        """
        if not LLM_AVAILABLE:
            return {
                "success": False,
                "error": "LLM client not available. Check Ollama installation."
            }
        
        try:
            # Build prompt for polishing
            prompt = f"""You are an expert resume writer. Rewrite these resume bullets to be:
- Stronger and more impactful
- ATS-optimized (include metrics and keywords)
- Concise but comprehensive
- Intensity level: {intensity}

Bullets:
{chr(10).join(f'- {b}' for b in bullets)}

Return as JSON array of polished bullets."""
            
            response = ask_llm(
                prompt,
                model=MODELS["polish"],
                temperature=0.7
            )
            
            # Parse response and extract bullet list
            try:
                polished = json.loads(response)
                if isinstance(polished, list):
                    return {"success": True, "bullets": polished}
                else:
                    return {"success": True, "bullets": [response]}
            except json.JSONDecodeError:
                return {"success": True, "bullets": [response]}
                
        except Exception as e:
            logger.error(f"✗ Error polishing bullets: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def tailor_resume(resume_text: str, job_description: str) -> Dict:
        """
        Tailor a resume to match a specific job description.
        
        Args:
            resume_text: Original resume content
            job_description: Target job description
            
        Returns:
            Dict with tailored resume
        """
        if not LLM_AVAILABLE:
            return {
                "success": False,
                "error": "LLM client not available. Check Ollama installation."
            }
        
        try:
            prompt = f"""You are an expert recruiter. Tailor this resume to match the job description.
Keep all real experience, but reframe bullets to highlight relevant keywords and skills from the job posting.
Don't add fake experience - only reword existing content.

ORIGINAL RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description}

Return the complete tailored resume in the same format."""
            
            response = ask_llm(
                prompt,
                model=MODELS["tailor"],
                temperature=0.6
            )
            
            return {"success": True, "tailored_resume": response}
            
        except Exception as e:
            logger.error(f"✗ Error tailoring resume: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def grade_resume(resume_text: str) -> Dict:
        """
        Grade and provide feedback on a resume.
        
        Args:
            resume_text: Resume content to grade
            
        Returns:
            Dict with score and feedback
        """
        if not LLM_AVAILABLE:
            return {
                "success": False,
                "error": "LLM client not available. Check Ollama installation."
            }
        
        try:
            prompt = f"""You are an expert recruiter and resume coach. Grade this resume on a scale of 0-100.
Provide:
1. Overall score (0-100)
2. Top 3 strengths
3. Top 3 areas for improvement
4. Actionable recommendations

RESUME:
{resume_text}

Return as JSON with keys: score, strengths, improvements, recommendations"""
            
            response = ask_llm(
                prompt,
                model=MODELS["polish"],
                temperature=0.5
            )
            
            try:
                grade_data = json.loads(response)
                return {"success": True, "grade": grade_data}
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "grade": {"feedback": response}
                }
                
        except Exception as e:
            logger.error(f"✗ Error grading resume: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def parse_to_pdf_format(resume_text: str) -> Dict:
        """
        Parse resume text into structured PDF format.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Dict with parsed resume structure
        """
        if not LLM_AVAILABLE:
            return {
                "success": False,
                "error": "LLM client not available. Check Ollama installation."
            }
        
        try:
            # This wraps the existing generate_resume.parse_resume_to_pdf_format
            parsed = parse_resume_to_pdf_format(resume_text)
            return {"success": True, "parsed_resume": parsed}
        except Exception as e:
            logger.error(f"✗ Error parsing resume: {e}")
            return {"success": False, "error": str(e)}
