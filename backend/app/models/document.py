"""
Document Model
===============
Stores uploaded documents (policies, manuals, reports, etc.)

Documents support version tracking — the 'version' field increments
when the same document is re-uploaded, and download_count tracks usage.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):
    """
    Database table: 'documents'

    Stores files like policies, manuals, technical reports, circulars, etc.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Document title
    title = Column(String(500), nullable=False, index=True)

    # Description of the document
    description = Column(Text, nullable=True)

    # Path to the actual file on disk
    file_path = Column(String(500), nullable=False)

    # Original filename uploaded by the user
    original_filename = Column(String(255), nullable=True)

    # File size in bytes
    file_size = Column(Integer, nullable=True)

    # MIME type (e.g., "application/pdf")
    mime_type = Column(String(100), nullable=True)

    # Category: "Policy", "Manual", "Report", "Circular", "Other"
    category = Column(String(100), nullable=True, default="Other")

    # Version tracking (incremented on re-upload)
    version = Column(Integer, default=1)

    # How many times this document was downloaded
    download_count = Column(Integer, default=0)

    # Who uploaded this document
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    uploaded_by_user = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title[:30]}...', v{self.version})>"
