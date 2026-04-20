"""
LLM Service - Handles all LLM calls for resume processing.
Uses the initialized Ollama service via Flask request context.
"""

import logging
import json
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

from config import MODELS


def _extract_json_from_response(response: str) -> Dict:
    """
    Extract and parse JSON from Ollama response.
    Handles markdown code blocks and malformed JSON.
    
    Args:
        response: Raw response text from Ollama
        
    Returns:
        Parsed JSON dict, or empty dict if parsing fails
    """
    try:
        # Remove markdown code blocks if present (```json ... ``` or ```...```)
        json_str = response.strip()
        if json_str.startswith('```'):
            # Extract content between backticks
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
            if match:
                json_str = match.group(1).strip()
        
        # Try to parse JSON directly (json.loads handles literal newlines fine)
        parsed = json.loads(json_str)
        return parsed
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        logger.error(f"Raw response: {response[:300]}")
        return None

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
        try:
            # Get Ollama service from Flask request context
            from flask import g
            logger.debug(f"polish_bullets: Checking for g.ollama_service...")
            if hasattr(g, 'ollama_service'):
                ollama = g.ollama_service
                logger.warning(f"✅ polish_bullets: Got Ollama service from g - instance {id(ollama)} with is_ready={ollama.is_ready}")
            else:
                # Fallback for non-request contexts (e.g., tests)
                logger.warning(f"⚠️  polish_bullets: g.ollama_service NOT FOUND - using fallback get_ollama_service()")
                from services.ollama_service import get_ollama_service
                ollama = get_ollama_service()
                logger.warning(f"⚠️  polish_bullets: Got Ollama service via fallback - instance {id(ollama)} with is_ready={ollama.is_ready}")
            
            logger.warning(f"🔍 polish_bullets: About to call ollama.generate() with is_ready={ollama.is_ready}")
            
            # Build prompt for polishing
            prompt = f"""You are an expert resume writer. Rewrite these resume bullets to be:
- Stronger and more impactful
- ATS-optimized (include metrics and keywords)
- Concise but comprehensive
- Intensity level: {intensity}

Bullets:
{chr(10).join(f'- {b}' for b in bullets)}

Return ONLY valid JSON array of polished bullets, like ["bullet1", "bullet2", ...].
DO NOT include any markdown, code blocks, or explanations. Just the JSON array."""
            
            logger.info("✨ Polishing bullets using Ollama...")
            result = ollama.generate(prompt, stream=False)
            
            if not result.get("success"):
                error_msg = result.get("error", "No response from Ollama. Please try again.")
                logger.error(f"✗ Ollama generation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            logger.debug(f"Ollama response structure: {result}")
            response = result.get("data", {}).get("response", "")
            
            if not response:
                logger.error("✗ No response text received from Ollama")
                logger.error(f"Full response: {result}")
                return {
                    "success": False,
                    "error": "No text response from Ollama. Please try again."
                }
            
            logger.debug(f"Raw Ollama response: {response[:500]}")
            
            # Parse response and extract bullet list
            polished = _extract_json_from_response(response)
            
            if polished and isinstance(polished, list):
                return {"success": True, "bullets": polished}
            elif polished and isinstance(polished, dict) and "bullets" in polished:
                return {"success": True, "bullets": polished["bullets"]}
            else:
                # If JSON parsing failed or response is not a list, return raw response as single bullet
                logger.warning(f"⚠️  Could not parse JSON response as list, using raw response")
                return {"success": True, "bullets": [response.strip()]}
                
        except Exception as e:
            logger.error(f"✗ Error polishing bullets: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def polish_resume(resume_text: str, intensity: str = "medium") -> Dict:
        """
        Polish an entire resume to be stronger and more ATS-optimized.
        
        Args:
            resume_text: Original resume content
            intensity: 'light', 'medium', or 'aggressive'
            
        Returns:
            Dict with polished resume and summary of changes
        """
        try:
            # Get Ollama service from Flask request context
            from flask import g
            logger.debug(f"polish_resume: Checking for g.ollama_service...")
            if hasattr(g, 'ollama_service'):
                ollama = g.ollama_service
                logger.warning(f"✅ polish_resume: Got Ollama service from g - instance {id(ollama)} with is_ready={ollama.is_ready}")
            else:
                # Fallback for non-request contexts (e.g., tests)
                logger.warning(f"⚠️  polish_resume: g.ollama_service NOT FOUND - using fallback get_ollama_service()")
                from services.ollama_service import get_ollama_service
                ollama = get_ollama_service()
                logger.warning(f"⚠️  polish_resume: Got Ollama service via fallback - instance {id(ollama)} with is_ready={ollama.is_ready}")
            
            logger.warning(f"🔍 polish_resume: About to call ollama.generate() with is_ready={ollama.is_ready}")
            
            # Import the prompt function
            from core.prompts import resume_polish_prompt
            
            prompt = resume_polish_prompt(resume_text, intensity)
            
            logger.info("✨ Polishing resume using Ollama...")
            result = ollama.generate(prompt, stream=False)
            
            if not result.get("success"):
                error_msg = result.get("error", "No response from Ollama. Please try again.")
                logger.error(f"✗ Ollama generation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            logger.debug(f"Ollama response structure: {result}")
            response = result.get("data", {}).get("response", "")
            
            if not response:
                logger.error("✗ No response text received from Ollama")
                logger.error(f"Full response: {result}")
                return {
                    "success": False,
                    "error": "No text response from Ollama. Please try again."
                }
            
            logger.debug(f"Polished resume length: {len(response)} characters")
            return {"success": True, "polished_resume": response}
            
        except Exception as e:
            logger.error(f"✗ Error polishing resume: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
        try:
            # Get Ollama service from Flask request context
            from flask import g
            logger.debug(f"tailor_resume: Checking for g.ollama_service...")
            if hasattr(g, 'ollama_service'):
                ollama = g.ollama_service
                logger.warning(f"✅ tailor_resume: Got Ollama service from g - instance {id(ollama)} with is_ready={ollama.is_ready}")
            else:
                # Fallback for non-request contexts (e.g., tests)
                logger.warning(f"⚠️  tailor_resume: g.ollama_service NOT FOUND - using fallback get_ollama_service()")
                from services.ollama_service import get_ollama_service
                ollama = get_ollama_service()
                logger.warning(f"⚠️  tailor_resume: Got Ollama service via fallback - instance {id(ollama)} with is_ready={ollama.is_ready}")
            
            logger.warning(f"🔍 tailor_resume: About to call ollama.generate() with is_ready={ollama.is_ready}")
            
            prompt = f"""You are an expert recruiter. Tailor this resume to match the job description.
Keep all real experience, but reframe bullets to highlight relevant keywords and skills from the job posting.
Don't add fake experience - only reword existing content.

ORIGINAL RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description}

Return the complete tailored resume in the same format."""
            
            logger.info("📋 Tailoring resume to job description using Ollama...")
            result = ollama.generate(prompt, stream=False)
            
            if not result.get("success"):
                error_msg = result.get("error", "No response from Ollama. Please try again.")
                logger.error(f"✗ Ollama generation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            logger.debug(f"Ollama response structure: {result}")
            response = result.get("data", {}).get("response", "")
            
            if not response:
                logger.error("✗ No response text received from Ollama")
                logger.error(f"Full response: {result}")
                return {
                    "success": False,
                    "error": "No text response from Ollama. Please try again."
                }
            
            logger.debug(f"Tailored resume length: {len(response)} characters")
            return {"success": True, "tailored_resume": response}
            
        except Exception as e:
            logger.error(f"✗ Error tailoring resume: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def grade_resume(resume_text: str) -> Dict:
        """
        Grade and provide feedback on a resume using Ollama.
        
        Args:
            resume_text: Resume content to grade
            
        Returns:
            Dict with score and feedback
        """
        try:
            # Get Ollama service from Flask request context
            from flask import g
            logger.debug(f"grade_resume: Checking for g.ollama_service...")
            if hasattr(g, 'ollama_service'):
                ollama = g.ollama_service
                logger.warning(f"✅ grade_resume: Got Ollama service from g - instance {id(ollama)} with is_ready={ollama.is_ready}")
            else:
                # Fallback for non-request contexts (e.g., tests)
                logger.warning(f"⚠️  grade_resume: g.ollama_service NOT FOUND - using fallback get_ollama_service()")
                from services.ollama_service import get_ollama_service
                ollama = get_ollama_service()
                logger.warning(f"⚠️  grade_resume: Got Ollama service via fallback - instance {id(ollama)} with is_ready={ollama.is_ready}")
            
            logger.warning(f"🔍 grade_resume: About to call ollama.generate() with is_ready={ollama.is_ready}")
            
            prompt = f"""You are an expert recruiter and resume coach. Grade this resume on a scale of 0-100.
Provide:
1. Overall score (0-100)
2. Top 3 strengths (as a list)
3. Top 3 areas for improvement (as a list)
4. Actionable recommendations (as a list)

RESUME:
{resume_text}

Return ONLY valid JSON with these exact keys: score, strengths, improvements, recommendations
Example format:
{{
  "score": 78,
  "strengths": ["bullet1", "bullet2", "bullet3"],
  "improvements": ["bullet1", "bullet2", "bullet3"],
  "recommendations": ["item1", "item2", "item3"]
}}"""
            
            logger.info("📊 Grading resume using Ollama...")
            result = ollama.generate(prompt, stream=False)
            
            if not result.get("success"):
                error_msg = result.get("error", "No response from Ollama. Please try again.")
                logger.error(f"✗ Ollama generation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            logger.debug(f"Ollama response structure: {result}")
            response = result.get("data", {}).get("response", "")
            
            if not response:
                logger.error("✗ No response text received from Ollama")
                logger.error(f"Full response: {result}")
                return {
                    "success": False,
                    "error": "No text response from Ollama. Please try again."
                }
            
            try:
                # Extract JSON from response
                import re
                # Try to parse response as-is first (handles newlines in JSON correctly)
                grade_data = None
                try:
                    grade_data = json.loads(response)
                except json.JSONDecodeError:
                    # If that fails, try extracting JSON block
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        grade_data = json.loads(json_str)
                    else:
                        raise json.JSONDecodeError("No JSON object found in response", response, 0)
                
                # Validate required fields
                required_fields = ['score', 'strengths', 'improvements', 'recommendations']
                for field in required_fields:
                    if field not in grade_data:
                        grade_data[field] = grade_data.get(field, 0 if field == 'score' else [])
                
                logger.info(f"✓ Resume graded: {grade_data.get('score', 0)}/100")
                return {"success": True, "grade": grade_data}
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"✗ Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response}")
                # Return failure instead of fallback response
                return {
                    "success": False,
                    "error": f"Failed to parse resume grading response: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"✗ Error grading resume: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def parse_to_pdf_format(resume_text: str) -> Dict:
        """
        Parse resume text into structured PDF format.
        Uses improved prompt that ensures all data is captured correctly.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Dict with parsed resume structure matching ResumData format
        """
        try:
            # Get Ollama service from Flask request context
            from flask import g
            logger.debug(f"parse_to_pdf_format: Checking for g.ollama_service...")
            if hasattr(g, 'ollama_service'):
                ollama = g.ollama_service
                logger.warning(f"✅ parse_to_pdf_format: Got Ollama service from g - instance {id(ollama)} with is_ready={ollama.is_ready}")
            else:
                # Fallback for non-request contexts (e.g., tests)
                logger.warning(f"⚠️  parse_to_pdf_format: g.ollama_service NOT FOUND - using fallback get_ollama_service()")
                from services.ollama_service import get_ollama_service
                ollama = get_ollama_service()
                logger.warning(f"⚠️  parse_to_pdf_format: Got Ollama service via fallback - instance {id(ollama)} with is_ready={ollama.is_ready}")
            
            logger.warning(f"🔍 parse_to_pdf_format: About to call ollama.generate() with is_ready={ollama.is_ready}")
            
            # Use improved prompt that specifies exact JSON structure
            from core.prompts import parse_to_pdf_format_prompt
            prompt = parse_to_pdf_format_prompt(resume_text)
            
            logger.info("📄 Parsing resume into structured format using Ollama...")
            result = ollama.generate(prompt, stream=False)
            
            if not result.get("success"):
                error_msg = result.get("error", "No response from Ollama. Please try again.")
                logger.error(f"✗ Ollama generation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            
            logger.debug(f"Ollama response structure: {result}")
            response = result.get("data", {}).get("response", "")
            
            if not response:
                logger.error("✗ No response text received from Ollama")
                logger.error(f"Full response: {result}")
                return {
                    "success": False,
                    "error": "No text response from Ollama. Please try again."
                }
            
            logger.debug(f"Raw Ollama response: {response[:500]}")
            logger.info(f"Response length: {len(response)} characters")
            
            # Parse response and extract structure using robust JSON parser
            parsed = _extract_json_from_response(response)
            
            if parsed:
                logger.info(f"✅ Successfully parsed resume structure from Ollama")
                # Validate parsed data has expected top-level keys
                logger.info(f"Parsed keys: {list(parsed.keys())}")
                if 'contact' in parsed:
                    logger.info(f"Contact name: {parsed.get('contact', {}).get('name', 'NOT FOUND')}")
                if 'work_experience' in parsed:
                    logger.info(f"Work experience entries: {len(parsed.get('work_experience', []))}")
                if 'projects' in parsed:
                    logger.info(f"Projects: {len(parsed.get('projects', []))}")
                return {"success": True, "parsed_resume": parsed}
            else:
                logger.error(f"⚠️  Failed to parse JSON from response")
                logger.error(f"Raw response: {response[:500]}")
                # Return failure - don't try to work with unparsable data
                return {
                    "success": False,
                    "error": "Failed to parse resume structure into JSON"
                }
                
        except Exception as e:
            logger.error(f"✗ Error parsing resume: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
