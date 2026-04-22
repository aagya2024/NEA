"""
Document Schemas
=================
Request/response schemas for document management.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentCreate(BaseModel):
    """Schema for document metadata (file is uploaded separately)."""
    title: str
    description: Optional[str] = None
    category: str = "Other"


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for a single document."""
    id: int
    title: str
    description: Optional[str] = None
    file_path: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    category: Optional[str] = None
    version: int = 1
    download_count: int = 0
    uploaded_by: int
    uploader_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Paginated document list response."""
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int
