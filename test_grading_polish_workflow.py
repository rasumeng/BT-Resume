#!/usr/bin/env python3
"""
Test script: Load Grace's Resume, grade it, polish it, and check for errors.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_resume(filename: str) -> Dict[str, Any]:
    """Get resume content."""
    print(f"\n{'='*70}")
    print(f"📖 STEP 1: Loading {filename}")
    print(f"{'='*70}")
    
    response = requests.get(f"{BASE_URL}/get-resume", params={"filename": filename})
    result = response.json()
    
    if result.get("success"):
        print(f"✅ Successfully loaded {filename}")
        print(f"   Content length: {len(result.get('content', ''))} chars")
        return result
    else:
        print(f"❌ Failed to load resume: {result.get('error')}")
        return result

def test_grade_resume(resume_text: str) -> Dict[str, Any]:
    """Grade the resume."""
    print(f"\n{'='*70}")
    print(f"⭐ STEP 2: Grading Resume")
    print(f"{'='*70}")
    
    payload = {
        "resume_text": resume_text
    }
    
    response = requests.post(f"{BASE_URL}/grade-resume", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ Successfully graded resume")
        grade_data = result.get("grade", {})
        print(f"   Overall Score: {grade_data.get('overall_score', 'N/A')}")
        print(f"   Strengths: {grade_data.get('strengths', ['None provided'])[:2]}")
        print(f"   Improvements: {grade_data.get('improvements', ['None provided'])[:2]}")
        return result
    else:
        print(f"❌ Failed to grade resume")
        print(f"   Error: {result.get('error')}")
        print(f"   Full response: {json.dumps(result, indent=2)}")
        return result

def test_polish_resume(resume_text: str, intensity: str = "medium") -> Dict[str, Any]:
    """Polish the resume."""
    print(f"\n{'='*70}")
    print(f"✨ STEP 3: Polishing Resume (intensity: {intensity})")
    print(f"{'='*70}")
    
    payload = {
        "resume_text": resume_text,
        "intensity": intensity
    }
    
    response = requests.post(f"{BASE_URL}/polish-resume", json=payload)
    result = response.json()
    
    if result.get("success"):
        polished_text = result.get("polished_resume", "")
        print(f"✅ Successfully polished resume")
        print(f"   Polished text length: {len(polished_text)} chars")
        return result
    else:
        print(f"❌ Failed to polish resume")
        print(f"   Error: {result.get('error')}")
        print(f"   Full response: {json.dumps(result, indent=2)}")
        return result

def test_save_polished_pdf(polished_text: str, filename: str = "Grace's Resume - Polished.pdf") -> Dict[str, Any]:
    """Save polished resume as PDF."""
    print(f"\n{'='*70}")
    print(f"💾 STEP 4: Saving Polished Resume as PDF")
    print(f"{'='*70}")
    
    payload = {
        "filename": filename,
        "text_content": polished_text
    }
    
    response = requests.post(f"{BASE_URL}/save-text-pdf", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ Successfully saved polished resume PDF")
        print(f"   Filename: {result.get('filename')}")
        print(f"   Path: {result.get('path')}")
        return result
    else:
        print(f"❌ Failed to save polished resume PDF")
        print(f"   Error: {result.get('error')}")
        print(f"   Full response: {json.dumps(result, indent=2)}")
        return result

def main():
    """Run the full workflow test."""
    print("\n" + "="*70)
    print("🚀 GRACE'S RESUME WORKFLOW TEST")
    print("="*70)
    
    # Step 1: Load resume
    resume_result = test_get_resume("Grace's Resume.txt")
    if not resume_result.get("success"):
        print("\n❌ Failed at Step 1. Aborting test.")
        return
    
    resume_text = resume_result.get("content")
    
    # Step 2: Grade resume
    grade_result = test_grade_resume(resume_text)
    if not grade_result.get("success"):
        print("\n⚠️  Grade failed - continuing anyway to test polish...")
    
    # Step 3: Polish resume
    time.sleep(1)  # Give backend a moment
    polish_result = test_polish_resume(resume_text)
    if not polish_result.get("success"):
        print("\n❌ Failed at Step 3 (Polish). Cannot continue.")
        return
    
    polished_text = polish_result.get("polished_resume")
    
    # Step 4: Save as PDF
    time.sleep(1)  # Give backend a moment
    pdf_result = test_save_polished_pdf(polished_text)
    if not pdf_result.get("success"):
        print("\n⚠️  PDF save failed - workflow partially complete")
    
    # Final summary
    print(f"\n{'='*70}")
    print("📊 WORKFLOW SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Load Resume:    {'PASS' if resume_result.get('success') else 'FAIL'}")
    print(f"✅ Grade Resume:   {'PASS' if grade_result.get('success') else 'FAIL'}")
    print(f"✅ Polish Resume:  {'PASS' if polish_result.get('success') else 'FAIL'}")
    print(f"✅ Save PDF:       {'PASS' if pdf_result.get('success') else 'FAIL'}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
