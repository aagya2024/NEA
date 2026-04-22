"""
Recruitment Routes
===================
Endpoints: GET /recruitment, POST /recruitment, PUT /recruitment/{id},
           DELETE /recruitment/{id}, POST /recruitment/{id}/apply,
           GET /recruitment/{id}/applications, PUT /applications/{id}/status
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.recruitment import (
    RecruitmentCreate, RecruitmentUpdate, RecruitmentResponse,
    RecruitmentListResponse, ApplicationCreate, ApplicationResponse,
    ApplicationStatusUpdate,
)
from app.services import recruitment_service
from app.utils.security import get_current_user
from app.utils.file_handler import save_upload
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter(prefix="/api/recruitment", tags=["Recruitment"])


@router.get("", response_model=RecruitmentListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    jobs, total = recruitment_service.get_jobs(db, page, per_page, status, department, search)
    items = []
    for j in jobs:
        resp = RecruitmentResponse.model_validate(j)
        resp.poster_name = j.poster.full_name if j.poster else None
        resp.application_count = len(j.applications) if j.applications else 0
        items.append(resp)
    return RecruitmentListResponse(jobs=items, total=total, page=page, per_page=per_page)


@router.get("/{job_id}", response_model=RecruitmentResponse)
def get_job(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = recruitment_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    resp = RecruitmentResponse.model_validate(job)
    resp.poster_name = job.poster.full_name if job.poster else None
    resp.application_count = len(job.applications) if job.applications else 0
    return resp


@router.post("", response_model=RecruitmentResponse, status_code=201)
def create_job(
    data: RecruitmentCreate,
    current_user: User = Depends(require_permission("manage_recruitment")),
    db: Session = Depends(get_db),
):
    job = recruitment_service.create_job(db, data, current_user.id)
    return RecruitmentResponse.model_validate(job)


@router.put("/{job_id}", response_model=RecruitmentResponse)
def update_job(
    job_id: int, data: RecruitmentUpdate,
    _=Depends(require_permission("manage_recruitment")),
    db: Session = Depends(get_db),
):
    job = recruitment_service.update_job(db, job_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return RecruitmentResponse.model_validate(job)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    _=Depends(require_permission("manage_recruitment")),
    db: Session = Depends(get_db),
):
    if not recruitment_service.delete_job(db, job_id):
        raise HTTPException(status_code=404, detail="Job posting not found")
    return {"message": "Job posting deleted"}


# ---- Applications ----

@router.post("/{job_id}/apply", response_model=ApplicationResponse, status_code=201)
async def apply_for_job(
    job_id: int,
    cover_letter: Optional[str] = None,
    cv: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = recruitment_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    if job.status != "open":
        raise HTTPException(status_code=400, detail="Job posting is no longer accepting applications")

    cv_path = None
    if cv and cv.filename:
        cv_path = await save_upload(cv, subfolder="cvs", allowed_categories=["document"])

    application = recruitment_service.submit_application(
        db, job_id, current_user.id, cover_letter, cv_path
    )
    if not application:
        raise HTTPException(status_code=400, detail="You have already applied for this position")

    resp = ApplicationResponse.model_validate(application)
    resp.job_title = job.title
    resp.applicant_name = current_user.full_name
    return resp


@router.get("/{job_id}/applications", response_model=list[ApplicationResponse])
def get_job_applications(
    job_id: int,
    _=Depends(require_permission("manage_recruitment")),
    db: Session = Depends(get_db),
):
    applications = recruitment_service.get_applications_for_job(db, job_id)
    items = []
    for a in applications:
        resp = ApplicationResponse.model_validate(a)
        resp.job_title = a.job.title if a.job else None
        resp.applicant_name = a.applicant.full_name if a.applicant else None
        items.append(resp)
    return items


@router.put("/applications/{app_id}/status", response_model=ApplicationResponse)
def update_application_status(
    app_id: int, data: ApplicationStatusUpdate,
    _=Depends(require_permission("manage_recruitment")),
    db: Session = Depends(get_db),
):
    application = recruitment_service.update_application_status(db, app_id, data)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return ApplicationResponse.model_validate(application)
