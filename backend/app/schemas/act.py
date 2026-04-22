"""
Act Schemas
============
Request/response schemas for acts, bylaws, and regulations.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ActCreate(BaseModel):
    """Schema for creating an act/bylaw entry."""
    title: str
    content: Optional[str] = None
    type: str = "Act"  # "Act", "Bylaw", "Regulation", "Directive", "Policy"
    tags: Optional[List[str]] = []
    year: Optional[int] = None


class ActUpdate(BaseModel):
    """Schema for updating an act."""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = None
    year: Optional[int] = None


class ActResponse(BaseModel):
    """Schema for a single act response."""
    id: int
    title: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    original_filename: Optional[str] = None
    type: str
    tags: Optional[List[str]] = []
    year: Optional[int] = None
    version: int = 1
    download_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ActListResponse(BaseModel):
    """Paginated act list response."""
    acts: List[ActResponse]
    total: int
    page: int
    per_page: int
