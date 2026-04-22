"""
News Model
==========
Stores news articles published on the NEA Intranet.

News articles can have rich text content, attachments (stored as JSON list
of file paths), and a publish/unpublish workflow.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class News(Base):
    """
    Database table: 'news'

    Stores internal news articles for the NEA organization.
    Only users with 'create_news' permission can create articles.
    """
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Article title
    title = Column(String(500), nullable=False, index=True)

    # Rich text content (HTML from the editor)
    content = Column(Text, nullable=False)

    # Category (e.g., "General", "Technical", "Administrative")
    category = Column(String(100), nullable=True, default="General")

    # URL-friendly slug generated from the title
    slug = Column(String(500), unique=True, nullable=True, index=True)

    # JSON list of attachment file paths: ["/uploads/news/file1.pdf", ...]
    attachments = Column(JSON, nullable=True, default=list)

    # Featured image path
    featured_image = Column(String(500), nullable=True)

    # Publish workflow
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Author (the user who created this article)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # View counter
    view_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    author = relationship("User", back_populates="news_articles")

    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title[:30]}...', published={self.is_published})>"
