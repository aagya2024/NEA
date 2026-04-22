"""
Notice Schemas
===============
Request/response schemas for notices/announcements.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NoticeCreate(BaseModel):
    """Schema for creating a notice."""
    title: str
    content: str
    type: str = "internal"  # "internal" or "public"
    priority: str = "medium"  # "low", "medium", "high", "urgent"
    expires_at: Optional[datetime] = None


class NoticeUpdate(BaseModel):
    """Schema for updating a notice."""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    expires_at: Optional[datetime] = None


class NoticeResponse(BaseModel):
    """Schema for a single notice response."""
    id: int
    title: str
    content: str
    type: str
    priority: str
    attachment: Optional[str] = None
    expires_at: Optional[datetime] = None
    author_id: int
    author_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NoticeListResponse(BaseModel):
    """Paginated notice list response."""
    notices: List[NoticeResponse]
    total: int
    page: int
    per_page: int
