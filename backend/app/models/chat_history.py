"""
Chat History Model
===================
Stores conversation logs between users and the AI knowledge assistant.

Each row represents one exchange (user message + AI response).
Sources are stored as JSON to track which documents the AI referenced.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ChatHistory(Base):
    """
    Database table: 'chat_history'

    Logs every interaction with the AI chatbot for audit and history.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Which user asked this question
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # The user's question/message
    message = Column(Text, nullable=False)

    # The AI's response
    response = Column(Text, nullable=True)

    # Sources used by RAG: [{"title": "...", "chunk": "...", "score": 0.92}, ...]
    sources = Column(JSON, nullable=True, default=list)

    # Session ID to group messages in one conversation
    session_id = Column(String(100), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ---- Relationships ----
    user = relationship("User", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id})>"
