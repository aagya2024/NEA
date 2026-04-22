"""
Chat Schemas
=============
Request/response schemas for the AI knowledge assistant chatbot.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatSource(BaseModel):
    """A single source document referenced by the AI."""
    title: str
    chunk: Optional[str] = None
    score: Optional[float] = None


class ChatRequest(BaseModel):
    """Schema for sending a message to the AI chatbot."""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for AI chatbot response."""
    message: str
    response: str
    sources: List[ChatSource] = []
    session_id: Optional[str] = None


class ChatHistoryItem(BaseModel):
    """Schema for a single chat history entry."""
    id: int
    message: str
    response: Optional[str] = None
    sources: Optional[List[dict]] = []
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Paginated chat history response."""
    messages: List[ChatHistoryItem]
    total: int
    page: int
    per_page: int
