"""
File Handler Utilities
======================
Handles file uploads, downloads, and validation for the NEA Intranet Portal.

USAGE:
    from app.utils.file_handler import save_upload, get_file_path, validate_file_type
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile, HTTPException, status

from app.config import settings

# Allowed file extensions by category
ALLOWED_EXTENSIONS = {
    "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "archive": [".zip", ".rar", ".7z"],
}

# Flatten all allowed extensions into one set
ALL_ALLOWED = {ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts}


def ensure_upload_dir() -> Path:
    """Create the upload directory if it doesn't exist."""
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to avoid collisions.
    
    Example:
        "report.pdf" -> "a1b2c3d4-e5f6-7890-abcd-ef1234567890_report.pdf"
    """
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    safe_name = Path(original_filename).stem.replace(" ", "_")[:50]
    return f"{unique_id}_{safe_name}{ext}"


def validate_file_type(filename: str, allowed_categories: Optional[List[str]] = None) -> bool:
    """
    Check if a file's extension is in the allowed list.
    
    Args:
        filename: The original filename
        allowed_categories: List of categories to allow (e.g., ["document", "image"])
                           If None, all categories are allowed.
    """
    ext = Path(filename).suffix.lower()
    
    if allowed_categories:
        allowed = {e for cat in allowed_categories if cat in ALLOWED_EXTENSIONS 
                   for e in ALLOWED_EXTENSIONS[cat]}
    else:
        allowed = ALL_ALLOWED
    
    return ext in allowed


def validate_file_size(file_size: int) -> bool:
    """Check if file size is within the configured limit."""
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    return file_size <= max_bytes


async def save_upload(
    file: UploadFile,
    subfolder: str = "general",
    allowed_categories: Optional[List[str]] = None,
) -> str:
    """
    Save an uploaded file to disk.
    
    Args:
        file: The uploaded file from FastAPI
        subfolder: Subfolder within uploads (e.g., "documents", "avatars")
        allowed_categories: File type categories to allow
    
    Returns:
        The relative path to the saved file (for storing in the database)
    
    Raises:
        HTTPException if file type or size is invalid
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )
    
    # Validate file type
    if not validate_file_type(file.filename, allowed_categories):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {ALL_ALLOWED}",
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )
    
    # Create subfolder
    upload_dir = ensure_upload_dir() / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    unique_name = generate_unique_filename(file.filename)
    file_path = upload_dir / unique_name
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return relative path for database storage
    return f"{subfolder}/{unique_name}"


def get_file_path(relative_path: str) -> Path:
    """
    Get the full filesystem path for a stored file.
    
    Args:
        relative_path: The path stored in the database
    
    Returns:
        Full Path object
    
    Raises:
        HTTPException if file doesn't exist
    """
    full_path = Path(settings.UPLOAD_DIR) / relative_path
    
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return full_path


def delete_file(relative_path: str) -> bool:
    """
    Delete a file from disk.
    
    Returns True if deleted, False if file didn't exist.
    """
    full_path = Path(settings.UPLOAD_DIR) / relative_path
    if full_path.exists():
        full_path.unlink()
        return True
    return False
