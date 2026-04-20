#!/usr/bin/env python
"""
Test to verify the Polish Resume path fix works correctly
Tests that the app will now find files at the correct Windows paths
"""

import json
import requests
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000/api"

def test_path_resolution():
    """
    Verify that the backend returns the correct Windows path
    that will work with File() constructor in Flutter
    """
    
    print("\n" + "="*70)
    print("PATH RESOLUTION TEST")
    print("="*70)
    
    sample_resume = """
JANE DOE
jane.doe@example.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced project manager with expertise in leading teams.

EXPERIENCE
Project Manager - Tech Company
2020-Present
- Managed 10+ person teams
- Delivered projects on time
- Improved productivity

SKILLS
Project Management, Agile, Leadership
"""
    
    print("\n[TEST] Polish resume and save PDF...")
    print("-" * 70)
    
    # Step 1: Polish the resume
    polish_response = requests.post(
        f"{BASE_URL}/polish-resume",
        json={"resume_text": sample_resume, "intensity": "medium"},
        timeout=120
    )
    
    if polish_response.status_code != 200:
        print(f"❌ Polish failed: {polish_response.text}")
        return False
    
    polish_result = polish_response.json()
    polished_text = polish_result["polished_resume"]
    print(f"✓ Polish successful, {len(polished_text)} chars")
    
    # Step 2: Save as PDF
    import time
    timestamp = int(time.time() * 1000)
    filename = f"path_test_resume_{timestamp}.pdf"
    
    save_response = requests.post(
        f"{BASE_URL}/save-text-pdf",
        json={"filename": filename, "text_content": polished_text},
        timeout=120
    )
    
    if save_response.status_code != 200:
        print(f"❌ Save failed: {save_response.text}")
        return False
    
    save_result = save_response.json()
    
    if not save_result.get("success"):
        print(f"❌ Save returned success=false: {save_result}")
        return False
    
    backend_path = save_result.get("path")
    print(f"✓ Backend returned path: {backend_path}")
    
    # Step 3: Verify the file exists at the backend's path
    if not os.path.exists(backend_path):
        print(f"❌ File not found at backend path: {backend_path}")
        return False
    
    file_size = os.path.getsize(backend_path)
    print(f"✓ File exists: {file_size} bytes")
    
    # Step 4: Test Windows path compatibility
    # This is what Flutter will do now - use the backend path directly
    flutter_file = Path(backend_path)
    if not flutter_file.exists():
        print(f"❌ Path object reports file missing: {flutter_file}")
        return False
    
    print(f"✓ Path object (Flutter compatible) found file")
    
    # Step 5: Verify it's a valid PDF
    with open(backend_path, 'rb') as f:
        header = f.read(4)
        if header != b'%PDF':
            print(f"❌ Invalid PDF file")
            return False
    
    print(f"✓ Valid PDF file (magic bytes verified)")
    
    print("\n" + "="*70)
    print("✓ PATH RESOLUTION TEST PASSED")
    print("="*70)
    print("\nBackend path resolution is correct!")
    print(f"Flutter app will now successfully find files at:")
    print(f"  {backend_path}")
    
    return True

if __name__ == "__main__":
    success = test_path_resolution()
    exit(0 if success else 1)
