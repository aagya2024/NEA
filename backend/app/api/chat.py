"""
Chat Routes
============
Endpoints for the AI knowledge assistant chatbot.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services import chat_service
from app.utils.security import get_current_user
from app.middleware.rate_limiter import rate_limit
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])


@router.post("", response_model=ChatResponse)
def send_message(
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_user),
    _rate=Depends(rate_limit(max_requests=20, window_seconds=60)),
    db: Session = Depends(get_db),
):
    """Send a message to the AI knowledge assistant."""
    return chat_service.send_message(
        db, current_user, chat_data.message, chat_data.session_id
    )


@router.get("/history", response_model=ChatHistoryResponse)
def get_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's chat history."""
    return chat_service.get_chat_history(db, current_user, page, per_page, session_id)


@router.post("/reindex")
def trigger_reindex(
    _=Depends(require_permission("reindex_ai")),
):
    """Trigger re-indexing of all documents for the AI pipeline."""
    return {
        "message": "Re-indexing is not yet implemented. "
                   "It will rebuild the vector store from all documents.",
        "status": "pending_implementation",
    }
