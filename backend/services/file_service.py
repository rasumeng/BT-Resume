"""
File Service - Handles resume file operations.
Responsible for: listing, loading, saving, and deleting resumes.
"""

import os
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from config import get_resumes_dir, get_outputs_dir

class FileService:
    """Service for managing resume files."""
    
    @staticmethod
    def list_resumes():
        """
        List all resumes in the resumes folder.
        Returns list of files with metadata.
        """
        try:
            resumes_dir = get_resumes_dir()
            files = []
            
            # Get .txt and .pdf files (exclude .json metadata files)
            for file in resumes_dir.iterdir():
                if file.is_file() and not file.name.endswith('.json'):
                    files.append({
                        "name": file.name,
                        "path": str(file),
                        "size": file.stat().st_size,
                        "modified": file.stat().st_mtime,
                        "created": file.stat().st_ctime
                    })
            
            # Sort by modified time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            logger.info(f"✓ Listed {len(files)} resumes")
            return {"success": True, "resumes": files}
        except Exception as e:
            logger.error(f"✗ Error listing resumes: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_resume(filename):
        """
        Load a resume file content.
        
        Args:
            filename: Name of the resume file
            
        Returns:
            File content as string
        """
        try:
            resumes_dir = get_resumes_dir()
            file_path = resumes_dir / filename
            
            # Security: Prevent path traversal
            if not file_path.parent == resumes_dir:
                raise ValueError("Invalid file path")
            
            if not file_path.exists():
                raise FileNotFoundError(f"Resume not found: {filename}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"✓ Loaded resume: {filename}")
            return {"success": True, "content": content, "filename": filename}
        except FileNotFoundError as e:
            logger.error(f"✗ File not found: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"✗ Error loading resume: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def save_resume_pdf(filename, resume_text):
        """
        Generate and save a PDF resume.
        
        Args:
            filename: Output filename (should end with .pdf)
            resume_text: Parsed resume text (JSON format from core logic)
            
        Returns:
            Path to saved PDF
        """
        try:
            from generate_resume import load_resume_data, generate_pdf
            import json
            
            outputs_dir = get_outputs_dir()
            output_path = outputs_dir / filename
            
            # Parse resume text if it's JSON
            if isinstance(resume_text, str):
                try:
                    resume_dict = json.loads(resume_text)
                except json.JSONDecodeError:
                    raise ValueError("Resume text must be valid JSON")
            else:
                resume_dict = resume_text
            
            # Load data into PDF generator
            load_resume_data(resume_dict)
            
            # Generate PDF
            generate_pdf(str(output_path))
            
            logger.info(f"✓ Generated PDF: {filename}")
            return {
                "success": True,
                "filename": filename,
                "path": str(output_path)
            }
        except Exception as e:
            logger.error(f"✗ Error generating PDF: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def update_resume(filename, content):
        """
        Update an existing resume file.
        
        Args:
            filename: Name of the resume file
            content: New content
            
        Returns:
            Confirmation
        """
        try:
            resumes_dir = get_resumes_dir()
            file_path = resumes_dir / filename
            
            # Security: Prevent path traversal
            if not file_path.parent == resumes_dir:
                raise ValueError("Invalid file path")
            
            if not file_path.exists():
                raise FileNotFoundError(f"Resume not found: {filename}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✓ Updated resume: {filename}")
            return {"success": True, "filename": filename}
        except Exception as e:
            logger.error(f"✗ Error updating resume: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def delete_resume(filename):
        """
        Delete a resume file.
        
        Args:
            filename: Name of the resume file
            
        Returns:
            Confirmation
        """
        try:
            resumes_dir = get_resumes_dir()
            file_path = resumes_dir / filename
            
            # Security: Prevent path traversal
            if not file_path.parent == resumes_dir:
                raise ValueError("Invalid file path")
            
            if not file_path.exists():
                raise FileNotFoundError(f"Resume not found: {filename}")
            
            os.remove(file_path)
            
            # Also delete associated JSON metadata if it exists
            json_path = file_path.with_suffix('.json')
            if json_path.exists():
                os.remove(json_path)
            
            logger.info(f"✓ Deleted resume: {filename}")
            return {"success": True, "deleted": filename}
        except Exception as e:
            logger.error(f"✗ Error deleting resume: {e}")
            return {"success": False, "error": str(e)}
