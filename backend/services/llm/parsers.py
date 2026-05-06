"""
JSON response parsers - Handles extraction and parsing of structured data from LLM responses.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def extract_json_from_response(response: str) -> Optional[Dict]:
    """
    Extract and parse JSON from Ollama response.
    Handles markdown code blocks, explanatory text, and malformed JSON.
    
    Args:
        response: Raw response text from Ollama
        
    Returns:
        Parsed JSON dict/list, or None if parsing fails
    """
    try:
        json_str = response.strip()
        
        # First, try to find JSON in code blocks (```json ... ``` or ```...```)
        # This handles: "Some text\n```json\n{...}\n```\nMore text"
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', json_str)
        if match:
            json_str = match.group(1).strip()
        # If no code block, try to find raw JSON object or array
        # This handles: "Some text {json} more text"
        elif not json_str.startswith('{') and not json_str.startswith('['):
            # Look for JSON object
            json_match = re.search(r'\{[\s\S]*\}(?=\s*(?:```|$))', json_str)
            if not json_match:
                # Look for JSON array
                json_match = re.search(r'\[[\s\S]*\](?=\s*(?:```|$))', json_str)
            if json_match:
                json_str = json_match.group(0)
        
        # Try to parse JSON
        parsed = json.loads(json_str)
        return parsed
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        logger.error(f"Raw response: {response[:300]}")
        return None


def validate_parsed_resume(parsed: Dict) -> bool:
    """
    Validate that parsed resume has expected structure.
    
    Args:
        parsed: Parsed resume dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(parsed, dict):
        return False
    
    required_keys = ['contact', 'work_experience', 'education']
    return all(key in parsed for key in required_keys)


def extract_bullet_list(response: str) -> Optional[List[str]]:
    """
    Extract bullet points from LLM response.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        List of bullet points, or None if parsing fails
    """
    parsed = extract_json_from_response(response)
    
    if parsed is None:
        return None
    
    # Handle different response formats
    if isinstance(parsed, list):
        return [str(b).strip() for b in parsed if b]
    
    if isinstance(parsed, dict):
        if "bullets" in parsed:
            bullet_list = parsed.get("bullets", [])
            if isinstance(bullet_list, list):
                return [str(b).strip() for b in bullet_list if b]
    
    return None


def extract_grade_data(response: str) -> Optional[Dict]:
    """
    Extract grade data from LLM response.
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Grade data dictionary with score, strengths, improvements, recommendations
    """
    try:
        # Try to parse response as-is first
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
        
        return grade_data
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"❌ Failed to parse grade data: {e}")
        return None
