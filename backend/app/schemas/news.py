"""
News Schemas
=============
Request/response schemas for news articles.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NewsCreate(BaseModel):
    """Schema for creating a news article."""
    title: str
    content: str
    category: Optional[str] = "General"
    is_published: bool = False


class NewsUpdate(BaseModel):
    """Schema for updating a news article."""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None


class NewsResponse(BaseModel):
    """Schema for a single news article response."""
    id: int
    title: str
    content: str
    category: Optional[str] = None
    slug: Optional[str] = None
    attachments: Optional[List[str]] = []
    featured_image: Optional[str] = None
    is_published: bool
    published_at: Optional[datetime] = None
    author_id: int
    author_name: Optional[str] = None
    view_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    """Paginated news list response."""
    news: List[NewsResponse]
    total: int
    page: int
    per_page: int
