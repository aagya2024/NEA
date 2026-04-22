"""
Notice Model
=============
Stores notices/announcements on the NEA Intranet.

Notices differ from news in that they can have:
- Type: internal (only employees) or public
- Priority levels (low, medium, high, urgent)
- Expiry dates (auto-hide after expiry)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Notice(Base):
    """
    Database table: 'notices'

    Notices are time-sensitive announcements with priority levels.
    """
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Notice title
    title = Column(String(500), nullable=False, index=True)

    # Notice content (can be rich text)
    content = Column(Text, nullable=False)

    # Type: 'internal' (employees only) or 'public'
    type = Column(String(20), nullable=False, default="internal")

    # Priority: 'low', 'medium', 'high', 'urgent'
    priority = Column(String(20), nullable=False, default="medium")

    # Attachment file path (e.g., PDF notice scan)
    attachment = Column(String(500), nullable=True)

    # When this notice expires (auto-hidden after this date)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Author who created this notice
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    author = relationship("User", back_populates="notices")

    def __repr__(self):
        return f"<Notice(id={self.id}, title='{self.title[:30]}...', priority='{self.priority}')>"
