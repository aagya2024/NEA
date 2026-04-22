"""
Form Schemas
=============
Request/response schemas for form templates.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FormCreate(BaseModel):
    """Schema for form metadata (file is uploaded separately)."""
    title: str
    description: Optional[str] = None
    category: str = "Other"


class FormUpdate(BaseModel):
    """Schema for updating form metadata."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class FormResponse(BaseModel):
    """Schema for a single form."""
    id: int
    title: str
    description: Optional[str] = None
    category: str
    file_path: str
    original_filename: Optional[str] = None
    version: int = 1
    download_count: int = 0
    uploaded_by: int
    uploader_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FormListResponse(BaseModel):
    """Paginated form list response."""
    forms: List[FormResponse]
    total: int
    page: int
    per_page: int
