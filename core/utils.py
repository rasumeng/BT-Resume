"""
Common utilities and helpers to reduce redundancy across core modules.
"""

import json
import re


# Error messages
OLLAMA_ERROR_MESSAGES = {
    "model_not_loaded": "❌ ERROR: Failed to get response from {model} (model may not be loaded)\n"
                       "❌ TIP: Check that {model} is loaded in Ollama by visiting http://localhost:11434/api/tags\n"
                       "❌ To load {model}, run: ollama pull {model}",
    "connection_failed": "❌ Cannot connect to Ollama at http://localhost:11434\n"
                        "❌ Make sure Ollama is running. Start it with: ollama serve",
    "timeout": "❌ Timeout waiting for Ollama to respond (model: {model}, timeout: {timeout}s)\n"
              "❌ This often means the model is still loading or system is slow.",
    "not_found": "Error from Ollama: Model '{model}' not found or not loaded\n"
                "Available models can be checked at: http://localhost:11434/api/tags\n"
                "Load the model with: ollama pull {model}",
}

SECTION_HEADER_SEPARATOR = "=" * 60


def format_error_message(error_type: str, **kwargs) -> str:
    """
    Format a standardized error message.
    
    Args:
        error_type: Key from OLLAMA_ERROR_MESSAGES
        **kwargs: Variables to substitute in the message
    
    Returns:
        Formatted error message
    """
    message = OLLAMA_ERROR_MESSAGES.get(error_type, "Unknown error")
    return message.format(**kwargs)


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{SECTION_HEADER_SEPARATOR}")
    print(title)
    print(SECTION_HEADER_SEPARATOR)


def extract_json_from_response(response: str) -> dict:
    """
    Extract and parse JSON from LLM response.
    
    Handles markdown code blocks and finds JSON object boundaries.
    
    Args:
        response: LLM response text
    
    Returns:
        Parsed JSON dict, or empty dict if parsing fails
    
    Raises:
        ValueError: If no JSON found or parsing fails
    """
    if not response:
        raise ValueError("Empty response")
    
    # Clean markdown code blocks
    clean_response = response
    if "```json" in clean_response:
        clean_response = clean_response.replace("```json", "").replace("```", "")
    elif "```" in clean_response:
        clean_response = clean_response.replace("```", "")
    
    # Find JSON boundaries
    start_idx = clean_response.find('{')
    end_idx = clean_response.rfind('}') + 1
    
    if start_idx == -1 or end_idx <= start_idx:
        raise ValueError("No JSON found in response")
    
    json_str = clean_response[start_idx:end_idx]
    
    # Replace literal newlines with escaped newlines for valid JSON
    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def create_bullet_points(bullet_dicts: list) -> list:
    """
    Create BulletPoint objects from list of dictionaries.
    
    Used to reduce redundancy in resume_model.py parsing.
    
    Args:
        bullet_dicts: List of dicts with 'text', 'has_location', 'has_date' keys
    
    Returns:
        List of BulletPoint objects
    """
    from .resume_model import BulletPoint
    
    bullets = []
    for bullet in bullet_dicts:
        if isinstance(bullet, dict):
            bullets.append(
                BulletPoint(
                    text=bullet.get("text", ""),
                    has_location=bullet.get("has_location", False),
                    has_date=bullet.get("has_date", False),
                )
            )
    return bullets


def normalize_whitespace(text: str) -> str:
    """Remove excess whitespace from text."""
    return re.sub(r"\s+", " ", text.strip())


def extract_urls(text: str) -> dict:
    """
    Extract common URLs from text (email, phone, LinkedIn, GitHub).
    
    Returns dict with keys: email, phone, linkedin, github
    """
    urls = {
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
    }
    
    # Email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if email_match:
        urls["email"] = email_match.group(0)
    
    # Phone
    phone_match = re.search(r"(?:\+\d{1,3}[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})", text)
    if phone_match:
        urls["phone"] = phone_match.group(0).strip()
    
    # LinkedIn
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-\.]+/?", text, re.IGNORECASE)
    if linkedin_match:
        url = linkedin_match.group(0).rstrip("/")
        if not url.startswith("http"):
            url = "https://" + url
        urls["linkedin"] = url
    
    # GitHub
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[\w\-\.]+/?", text, re.IGNORECASE)
    if github_match:
        url = github_match.group(0).rstrip("/")
        if not url.startswith("http"):
            url = "https://" + url
        urls["github"] = url
    
    return urls
