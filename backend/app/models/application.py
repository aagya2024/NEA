"""
Application Model
==================
Stores job applications submitted by employees for internal positions.

Each application links a user to a recruitment posting and tracks the
review status: pending → reviewed → shortlisted → accepted/rejected.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Application(Base):
    """
    Database table: 'applications'

    Tracks employee applications for internal job postings.
    """
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Which job posting this application is for
    recruitment_id = Column(Integer, ForeignKey("recruitment.id", ondelete="CASCADE"), nullable=False)

    # Who submitted this application
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Path to uploaded CV/resume
    cv_path = Column(String(500), nullable=True)

    # Cover letter text
    cover_letter = Column(Text, nullable=True)

    # Status: 'pending', 'reviewed', 'shortlisted', 'accepted', 'rejected'
    status = Column(String(20), nullable=False, default="pending")

    # Reviewer notes (visible only to HR)
    reviewer_notes = Column(Text, nullable=True)

    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    job = relationship("Recruitment", back_populates="applications")
    applicant = relationship("User", back_populates="applications")

    def __repr__(self):
        return f"<Application(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
