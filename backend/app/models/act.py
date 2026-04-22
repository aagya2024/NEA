"""
Act Model
==========
Stores Acts, Bylaws, and Regulations relevant to NEA.

These are legal/regulatory documents that employees need to reference.
Examples: Electricity Act 2049, NEA Service Bylaws, etc.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.database import Base


class Act(Base):
    """
    Database table: 'acts'

    Stores legal documents: Acts, Bylaws, Regulations, Directives.
    """
    __tablename__ = "acts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Title of the act/bylaw
    title = Column(String(500), nullable=False, index=True)

    # Full text content (if available)
    content = Column(Text, nullable=True)

    # Path to the PDF file
    file_path = Column(String(500), nullable=True)

    # Original filename
    original_filename = Column(String(255), nullable=True)

    # Type: "Act", "Bylaw", "Regulation", "Directive", "Policy"
    type = Column(String(50), nullable=False, default="Act")

    # Tags for search/filtering: ["electricity", "tariff", "distribution"]
    tags = Column(JSON, nullable=True, default=list)

    # Year of enactment or publication
    year = Column(Integer, nullable=True)

    # Version tracking
    version = Column(Integer, default=1)

    # Download count
    download_count = Column(Integer, default=0)

    # Who uploaded this (admin/super admin)
    uploaded_by = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Act(id={self.id}, title='{self.title[:30]}...', year={self.year})>"
