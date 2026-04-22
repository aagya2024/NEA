"""
Recruitment Model
==================
Stores internal job postings for the NEA organization.

HR managers create job postings, and employees can apply through
the internal portal. The status tracks the posting lifecycle:
open → closed → filled.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Recruitment(Base):
    """
    Database table: 'recruitment'

    Stores internal job/vacancy postings.
    """
    __tablename__ = "recruitment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Job title
    title = Column(String(500), nullable=False, index=True)

    # Job description (rich text)
    description = Column(Text, nullable=False)

    # Department offering the position
    department = Column(String(100), nullable=True)

    # Requirements / qualifications (rich text)
    requirements = Column(Text, nullable=True)

    # Number of positions available
    positions = Column(Integer, default=1)

    # Application deadline
    deadline = Column(DateTime(timezone=True), nullable=True)

    # Status: 'open', 'closed', 'filled', 'cancelled'
    status = Column(String(20), nullable=False, default="open")

    # Additional qualifications as JSON list
    qualifications = Column(JSON, nullable=True, default=list)

    # Who posted this job
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ---- Relationships ----
    poster = relationship("User", backref="job_postings")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recruitment(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"
