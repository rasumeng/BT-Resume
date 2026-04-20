#!/usr/bin/env python
"""
Test script to verify the Polish Resume feature works correctly
Tests the full workflow: resume parsing -> polishing -> PDF generation
"""

import json
import requests
import time
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000/api"
RESUMES_DIR = Path(os.path.expanduser("~")) / "Documents" / "Resume AI" / "resumes"

def log(msg, level="INFO"):
    """Simple logging"""
    print(f"[{level}] {msg}")

def test_health_check():
    """Step 1: Verify backend is healthy"""
    log("=" * 60)
    log("STEP 1: Checking backend health", level="TEST")
    log("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        log(f"Health check status: {response.status_code}")
        log(f"Response: {response.json()}")
        assert response.status_code == 200, "Backend not healthy"
        log("✓ Backend health check PASSED", level="PASS")
        return True
    except Exception as e:
        log(f"✗ Backend health check FAILED: {e}", level="ERROR")
        return False

def test_polish_resume():
    """Step 2: Test the polish resume endpoint"""
    log("=" * 60)
    log("STEP 2: Testing Polish Resume API", level="TEST")
    log("=" * 60)
    
    # Sample resume text
    sample_resume = """
JOHN DOE
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

SUMMARY
Experienced software engineer with 5 years of experience in full-stack development.

EXPERIENCE
Software Engineer - Tech Company Inc.
Jan 2020 - Present
- Developed backend services using Python and Flask
- Built responsive user interfaces with Flutter and Dart
- Wrote unit tests for critical components
- Collaborated with team members on various projects

Junior Developer - StartUp LLC
Jun 2018 - Dec 2019
- Worked on web applications
- Fixed bugs and improved performance
- Attended meetings and helped with tasks

EDUCATION
Bachelor of Science in Computer Science
State University, May 2018

SKILLS
Python, JavaScript, Flutter, Dart, Flask, React, SQL, Git
"""
    
    payload = {
        "resume_text": sample_resume,
        "intensity": "medium"
    }
    
    log(f"Sending polish request with {len(sample_resume)} character resume...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/polish-resume",
            json=payload,
            timeout=120  # Polish can take a while with LLM
        )
        
        log(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            log(f"Response keys: {list(result.keys())}")
            log(f"✓ Polish API returned successful response", level="PASS")
            
            if "polished_resume" in result:
                polished = result["polished_resume"]
                log(f"✓ Got polished text ({len(polished)} chars)", level="PASS")
                return True, result
            else:
                log(f"Response: {json.dumps(result, indent=2)}", level="ERROR")
                return False, result
        else:
            log(f"API error status: {response.status_code}", level="ERROR")
            try:
                log(f"Error response: {response.json()}", level="ERROR")
            except:
                log(f"Error response: {response.text}", level="ERROR")
            return False, None
            
    except Exception as e:
        log(f"✗ Polish API test FAILED: {e}", level="ERROR")
        import traceback
        traceback.print_exc()
        return False, None

def test_save_polished_pdf():
    """Step 3: Test saving polished resume as PDF"""
    log("=" * 60)
    log("STEP 3: Testing Save Polished Resume as PDF", level="TEST")
    log("=" * 60)
    
    sample_resume = """
JANE SMITH
jane.smith@email.com | (555) 987-6543

PROFESSIONAL SUMMARY
Results-driven project manager with 7 years experience in Agile environments.

EXPERIENCE
Project Manager - Digital Solutions Corp
Mar 2019 - Present
- Managed cross-functional teams of 10+ members
- Delivered projects on time and under budget
- Improved team productivity by 30%

Senior Associate - Consulting Group
Jan 2017 - Feb 2019
- Supported senior consultants on client engagements
- Conducted market research
- Prepared presentations and reports

EDUCATION
MBA in Business Administration
Tech University, 2016

SKILLS
Project Management, Agile, Leadership, Communication, Excel, PowerPoint
"""
    
    payload = {
        "filename": "test_polished_resume.pdf",
        "text_content": sample_resume
    }
    
    log(f"Sending save-text-pdf request...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/save-text-pdf",
            json=payload,
            timeout=120
        )
        
        log(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            log(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                saved_path = result.get("path")
                if saved_path:
                    log(f"✓ PDF saved at: {saved_path}", level="PASS")
                    
                    # Verify file exists
                    if os.path.exists(saved_path):
                        file_size = os.path.getsize(saved_path)
                        log(f"✓ File exists and is {file_size} bytes", level="PASS")
                        return True, saved_path
                    else:
                        log(f"✗ File not found at path: {saved_path}", level="ERROR")
                        return False, None
                else:
                    log(f"✗ No path in response", level="ERROR")
                    return False, None
            else:
                log(f"✗ PDF save returned success=false", level="ERROR")
                return False, None
        else:
            log(f"API error status: {response.status_code}", level="ERROR")
            try:
                log(f"Error response: {response.json()}", level="ERROR")
            except:
                log(f"Error response: {response.text}", level="ERROR")
            return False, None
            
    except Exception as e:
        log(f"✗ Save PDF test FAILED: {e}", level="ERROR")
        import traceback
        traceback.print_exc()
        return False, None

def test_full_polish_workflow():
    """Step 4: Full workflow - polish then save as PDF"""
    log("=" * 60)
    log("STEP 4: Testing Full Polish + PDF Workflow", level="TEST")
    log("=" * 60)
    
    sample_resume = """
ALEX JOHNSON
alex.j@email.com | (555) 456-7890 | GitHub: github.com/alexj

OBJECTIVE
Seeking a role where I can use my programming skills and help the company succeed.

EXPERIENCE
Software Engineer at WebTech Solutions
Aug 2021 - Present
- Made some improvements to the codebase
- Fixed some bugs
- Attended daily standups

Web Developer at Design Studio
Mar 2020 - Jul 2021
- Worked on website projects
- Did some HTML and CSS coding
- Helped with various tasks

EDUCATION
BS in Computer Science - Any State University (2019)
Some Online Courses in Web Development (2018-2019)

TECHNICAL SKILLS
Languages: Python, JavaScript, Java, C++
Web: HTML, CSS, JavaScript, React
Databases: MySQL, MongoDB
Tools: Git, Docker, Jenkins
"""
    
    log(f"Step 4a: Polish the resume...")
    success, polish_result = test_polish_resume()
    if not success:
        log("✗ Polish step failed", level="ERROR")
        return False
    
    if not polish_result or "polished_resume" not in polish_result:
        log("✗ No polished resume in result", level="ERROR")
        return False
    
    polished_text = polish_result["polished_resume"]
    log(f"Step 4b: Save polished resume as PDF...")
    
    payload = {
        "filename": "workflow_test_polished.pdf",
        "text_content": polished_text
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/save-text-pdf",
            json=payload,
            timeout=120
        )
        
        log(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                saved_path = result.get("path")
                log(f"PDF saved at: {saved_path}", level="PASS")
                
                if os.path.exists(saved_path):
                    file_size = os.path.getsize(saved_path)
                    log(f"✓ File verified: {file_size} bytes", level="PASS")
                    log("✓ FULL WORKFLOW TEST PASSED", level="PASS")
                    return True
                else:
                    log(f"✗ File not found: {saved_path}", level="ERROR")
                    return False
            else:
                log(f"✗ Save failed: {result}", level="ERROR")
                return False
        else:
            log(f"API error: {response.status_code}", level="ERROR")
            try:
                log(f"Error: {response.json()}", level="ERROR")
            except:
                log(f"Error: {response.text}", level="ERROR")
            return False
            
    except Exception as e:
        log(f"✗ Workflow test FAILED: {e}", level="ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    log("=" * 60)
    log("POLISH RESUME FEATURE TEST SUITE", level="INFO")
    log("=" * 60)
    log("")
    
    results = {
        "health_check": False,
        "polish_api": False,
        "save_pdf": False,
        "full_workflow": False
    }
    
    # Test 1: Health check
    results["health_check"] = test_health_check()
    if not results["health_check"]:
        log("\n✗ Backend not healthy. Cannot continue tests.", level="ERROR")
        return results
    
    log("")
    time.sleep(1)
    
    # Test 2: Polish API
    success, _ = test_polish_resume()
    results["polish_api"] = success
    
    log("")
    time.sleep(1)
    
    # Test 3: Save PDF
    success, _ = test_save_polished_pdf()
    results["save_pdf"] = success
    
    log("")
    time.sleep(1)
    
    # Test 4: Full workflow
    results["full_workflow"] = test_full_polish_workflow()
    
    # Summary
    log("")
    log("=" * 60)
    log("TEST SUMMARY", level="INFO")
    log("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        log(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    log("")
    if all_passed:
        log("✓ ALL TESTS PASSED", level="PASS")
    else:
        log(f"✗ {sum(1 for v in results.values() if not v)} TEST(S) FAILED", level="ERROR")
    
    return results

if __name__ == "__main__":
    main()
