"""
Recruitment Routes
===================
CRUD endpoints for job postings and job applications.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.recruitment import (
    RecruitmentCreate, RecruitmentUpdate, RecruitmentResponse, RecruitmentListResponse,
    ApplicationCreate, ApplicationStatusUpdate, ApplicationResponse,
)
from app.services import recruitment_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/recruitment", tags=["Recruitment"])


@router.get("", response_model=RecruitmentListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List job postings (paginated)."""
    return recruitment_service.get_jobs(db, page, per_page, status, department)


@router.get("/{job_id}", response_model=RecruitmentResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single job posting."""
    job = recruitment_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    
    result = RecruitmentResponse.model_validate(job)
    if job.poster:
        result.poster_name = job.poster.full_name
    result.application_count = len(job.applications) if job.applications else 0
    return result


@router.post("", response_model=RecruitmentResponse, status_code=201)
def create_job(
    job_data: RecruitmentCreate,
    current_user: User = Depends(require_permission("create_job")),
    db: Session = Depends(get_db),
):
    """Create a new job posting."""
    return recruitment_service.create_job(db, job_data, current_user)


@router.put("/{job_id}", response_model=RecruitmentResponse)
def update_job(
    job_id: int,
    job_data: RecruitmentUpdate,
    _=Depends(require_permission("edit_job")),
    db: Session = Depends(get_db),
):
    """Update a job posting."""
    return recruitment_service.update_job(db, job_id, job_data)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    _=Depends(require_permission("delete_job")),
    db: Session = Depends(get_db),
):
    """Delete a job posting."""
    recruitment_service.delete_job(db, job_id)
    return {"message": "Job posting deleted successfully"}


# ---- Application Endpoints ----

@router.post("/{job_id}/apply", response_model=ApplicationResponse, status_code=201)
async def apply_for_job(
    job_id: int,
    application: ApplicationCreate,
    cv: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply for a job posting."""
    result = await recruitment_service.apply_for_job(
        db, job_id, current_user, application.cover_letter, cv
    )
    resp = ApplicationResponse.model_validate(result)
    resp.applicant_name = current_user.full_name
    return resp


@router.get("/{job_id}/applications", response_model=list[ApplicationResponse])
def list_applications(
    job_id: int,
    _=Depends(require_permission("view_applications")),
    db: Session = Depends(get_db),
):
    """View all applications for a job posting (HR/Admin)."""
    applications = recruitment_service.get_applications(db, job_id)
    results = []
    for app in applications:
        resp = ApplicationResponse.model_validate(app)
        if app.applicant:
            resp.applicant_name = app.applicant.full_name
        if app.job:
            resp.job_title = app.job.title
        results.append(resp)
    return results


@router.put("/applications/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_data: ApplicationStatusUpdate,
    _=Depends(require_permission("approve_job")),
    db: Session = Depends(get_db),
):
    """Update an application's status (HR action)."""
    return recruitment_service.update_application_status(db, application_id, status_data)
