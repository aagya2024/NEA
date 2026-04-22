"""
Recruitment Schemas
====================
Request/response schemas for job postings and applications.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RecruitmentCreate(BaseModel):
    """Schema for creating a job posting."""
    title: str
    description: str
    department: Optional[str] = None
    requirements: Optional[str] = None
    positions: int = 1
    deadline: Optional[datetime] = None
    qualifications: Optional[List[str]] = []


class RecruitmentUpdate(BaseModel):
    """Schema for updating a job posting."""
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    requirements: Optional[str] = None
    positions: Optional[int] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    qualifications: Optional[List[str]] = None


class RecruitmentResponse(BaseModel):
    """Schema for a single job posting response."""
    id: int
    title: str
    description: str
    department: Optional[str] = None
    requirements: Optional[str] = None
    positions: int = 1
    deadline: Optional[datetime] = None
    status: str
    qualifications: Optional[List[str]] = []
    posted_by: int
    poster_name: Optional[str] = None
    application_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecruitmentListResponse(BaseModel):
    """Paginated job postings response."""
    jobs: List[RecruitmentResponse]
    total: int
    page: int
    per_page: int


# ---- Application Schemas ----

class ApplicationCreate(BaseModel):
    """Schema for submitting a job application."""
    cover_letter: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    """Schema for HR updating application status."""
    status: str  # "pending", "reviewed", "shortlisted", "accepted", "rejected"
    reviewer_notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Schema for a single application response."""
    id: int
    recruitment_id: int
    job_title: Optional[str] = None
    user_id: int
    applicant_name: Optional[str] = None
    cv_path: Optional[str] = None
    cover_letter: Optional[str] = None
    status: str
    reviewer_notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
