#!/usr/bin/env python3
"""
Test JSON extraction with direct function testing
"""

import json
import sys
import logging
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _extract_json_from_response(response: str) -> dict:
    """Extract JSON from response text (standalone copy for testing)"""
    if not response or not isinstance(response, str):
        return None
    
    # Remove markdown code block markers if present
    response = re.sub(r'```json\s*\n?', '', response)
    response = re.sub(r'```\s*$', '', response)
    
    # Try to parse as-is first
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object within the response
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    return None


def test_extraction():
    """Test JSON extraction"""
    
    logger.info("=" * 80)
    logger.info("JSON EXTRACTION TEST")
    logger.info("=" * 80)
    
    test_cases = [
        {
            "name": "Clean JSON",
            "response": json.dumps({
                "contact": {"name": "John Doe", "email": "john@example.com"},
                "work_experience": [{"position": "Engineer", "company": "TechCorp", "bullets": ["Achievement 1"]}],
                "projects": [],
                "education": [],
                "leadership": [],
                "skills": []
            }),
            "expect_name": "John Doe"
        },
        {
            "name": "JSON with explanation",
            "response": """Here's the parsed resume:

{
  "contact": {"name": "Jane Smith", "email": "jane@example.com"},
  "work_experience": [{"position": "Manager", "company": "Corp", "bullets": ["Led team"]}],
  "projects": [],
  "education": [],
  "leadership": [],
  "skills": []
}

Done!""",
            "expect_name": "Jane Smith"
        },
        {
            "name": "JSON in markdown code block",
            "response": """```json
{
  "contact": {"name": "Bob Johnson"},
  "work_experience": [],
  "projects": [],
  "education": [],
  "leadership": [],
  "skills": []
}
```""",
            "expect_name": "Bob Johnson"
        }
    ]
    
    logger.info("\n🧪 Testing JSON extraction...\n")
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        logger.info(f"Test {i}: {test['name']}")
        
        extracted = _extract_json_from_response(test["response"])
        
        if extracted:
            name = extracted.get("contact", {}).get("name")
            if name == test["expect_name"]:
                logger.info(f"  ✓ PASS - Extracted name: {name}\n")
            else:
                logger.error(f"  ✗ FAIL - Expected '{test['expect_name']}', got '{name}'\n")
                all_passed = False
        else:
            logger.error(f"  ✗ FAIL - Could not extract JSON\n")
            all_passed = False
    
    if all_passed:
        logger.info("=" * 80)
        logger.info("✅ ALL TESTS PASSED")
        logger.info("=" * 80)
        return True
    else:
        logger.error("=" * 80)
        logger.error("❌ SOME TESTS FAILED")
        logger.error("=" * 80)
        return False


if __name__ == "__main__":
    success = test_extraction()
    sys.exit(0 if success else 1)
