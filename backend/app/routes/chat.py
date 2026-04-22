"""
Chat Routes
============
Endpoints: POST /chat, GET /chat/history
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.services import chat_service
from app.utils.security import get_current_user
from app.middleware.rate_limiter import rate_limit_chat
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])


@router.post("", response_model=ChatResponse, dependencies=[Depends(rate_limit_chat)])
def send_message(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message to the AI knowledge assistant."""
    result = chat_service.chat_with_ai(
        db, current_user.id, data.message, data.session_id
    )
    return result


@router.get("/history")
def get_history(
    session_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's chat history."""
    chats = chat_service.get_chat_history(db, current_user.id, session_id, limit)
    return [
        {
            "id": c.id,
            "message": c.message,
            "response": c.response,
            "sources": c.sources,
            "session_id": c.session_id,
            "created_at": str(c.created_at),
        }
        for c in chats
    ]
