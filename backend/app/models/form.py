"""
Form Model
===========
Stores downloadable form templates (HR forms, finance forms, technical forms).

Employees can download these forms, fill them out, and submit them
through the appropriate channels.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Form(Base):
    """
    Database table: 'forms'

    Stores form templates organized by category (HR, Finance, Technical).
    """
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Form title (e.g., "Leave Application Form")
    title = Column(String(500), nullable=False, index=True)

    # Description / instructions
    description = Column(Text, nullable=True)

    # Category: "HR", "Finance", "Technical", "Administrative", "Other"
    category = Column(String(100), nullable=False, default="Other")

    # Path to the form file (PDF/DOCX)
    file_path = Column(String(500), nullable=False)

    # Original filename
    original_filename = Column(String(255), nullable=True)

    # Version (for updated forms)
    version = Column(Integer, default=1)

    # Download count
    download_count = Column(Integer, default=0)

    # Who uploaded this form
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    uploaded_by_user = relationship("User", back_populates="forms")

    def __repr__(self):
        return f"<Form(id={self.id}, title='{self.title[:30]}...', category='{self.category}')>"
