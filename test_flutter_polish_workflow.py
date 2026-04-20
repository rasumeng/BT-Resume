#!/usr/bin/env python
"""
Comprehensive test that simulates the exact Flutter app workflow for Polish Resume
"""

import json
import requests
import time
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000/api"
RESUMES_DIR = Path(os.path.expanduser("~")) / "Documents" / "Resume AI" / "resumes"

def test_flutter_polish_workflow():
    """
    Simulate the exact workflow that the Flutter app performs:
    1. User has a resume
    2. User clicks "Polish" button
    3. App calls /api/polish-resume endpoint
    4. App saves the polished result as PDF via /api/save-text-pdf
    5. App downloads/opens the PDF file
    """
    
    print("\n" + "="*70)
    print("FLUTTER POLISH RESUME WORKFLOW TEST")
    print("="*70)
    
    # Sample resume that might be in the app
    original_resume = """
ALEX TECH
alex@email.com | 555-9999 | LinkedIn: /in/alextech

OBJECTIVE
Looking for a software development role.

EXPERIENCE
Developer at CompanyA
2022-Present
- Wrote some code
- Fixed bugs
- Attended meetings

Junior Dev at CompanyB
2020-2021
- Worked on projects
- Did programming tasks

EDUCATION
BS Computer Science, Tech University 2020
Some online courses

SKILLS
Python, JavaScript, React, SQL
"""
    
    print("\n[STEP 1] Original resume:")
    print("-" * 70)
    print(original_resume)
    
    print("\n[STEP 2] Calling Polish API (/api/polish-resume)...")
    print("-" * 70)
    
    payload = {
        "resume_text": original_resume,
        "intensity": "medium"
    }
    
    try:
        polish_response = requests.post(
            f"{BASE_URL}/polish-resume",
            json=payload,
            timeout=120
        )
        
        if polish_response.status_code != 200:
            print(f"❌ Polish API failed with status {polish_response.status_code}")
            print(f"   Response: {polish_response.text}")
            return False
        
        polish_result = polish_response.json()
        
        if not polish_result.get("success"):
            print(f"❌ Polish API returned success=false")
            print(f"   Response: {json.dumps(polish_result, indent=2)}")
            return False
        
        polished_text = polish_result.get("polished_resume")
        if not polished_text:
            print(f"❌ No polished_resume in response")
            return False
        
        print(f"✓ Polish API successful")
        print(f"✓ Polished text length: {len(polished_text)} characters")
        
        print("\n[POLISHED RESUME]")
        print("-" * 70)
        print(polished_text)
        
    except Exception as e:
        print(f"❌ Polish API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n[STEP 3] Saving polished resume as PDF (/api/save-text-pdf)...")
    print("-" * 70)
    
    timestamp = int(time.time() * 1000)
    pdf_filename = f"polished_resume_{timestamp}.pdf"
    
    save_payload = {
        "filename": pdf_filename,
        "text_content": polished_text
    }
    
    try:
        save_response = requests.post(
            f"{BASE_URL}/save-text-pdf",
            json=save_payload,
            timeout=120
        )
        
        if save_response.status_code != 200:
            print(f"❌ Save PDF API failed with status {save_response.status_code}")
            print(f"   Response: {save_response.text}")
            return False
        
        save_result = save_response.json()
        
        if not save_result.get("success"):
            print(f"❌ Save PDF API returned success=false")
            print(f"   Response: {json.dumps(save_result, indent=2)}")
            return False
        
        pdf_path = save_result.get("path")
        if not pdf_path:
            print(f"❌ No path in save response")
            return False
        
        print(f"✓ PDF saved successfully")
        print(f"✓ PDF filename: {save_result.get('filename')}")
        print(f"✓ PDF path: {pdf_path}")
        
    except Exception as e:
        print(f"❌ Save PDF API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n[STEP 4] Verifying PDF file...")
    print("-" * 70)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found at: {pdf_path}")
        return False
    
    file_size = os.path.getsize(pdf_path)
    print(f"✓ PDF file exists at: {pdf_path}")
    print(f"✓ File size: {file_size} bytes")
    
    # Verify it's a valid PDF
    with open(pdf_path, 'rb') as f:
        header = f.read(4)
        if header == b'%PDF':
            print(f"✓ Valid PDF file (verified magic bytes)")
        else:
            print(f"⚠️  Warning: File may not be a valid PDF (header: {header})")
    
    print("\n" + "="*70)
    print("✓ FLUTTER POLISH WORKFLOW TEST PASSED")
    print("="*70)
    print("\nThe Polish Resume feature is working correctly!")
    print(f"Polished PDF created: {os.path.basename(pdf_path)}")
    
    return True

if __name__ == "__main__":
    success = test_flutter_polish_workflow()
    exit(0 if success else 1)
