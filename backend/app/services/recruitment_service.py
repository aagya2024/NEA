"""
Recruitment Service
====================
CRUD for job postings and application management.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.recruitment import Recruitment
from app.models.application import Application
from app.schemas.recruitment import RecruitmentCreate, RecruitmentUpdate, ApplicationStatusUpdate
from app.utils.logger import logger


# ---- Job Postings ----

def create_job(db: Session, data: RecruitmentCreate, posted_by: int) -> Recruitment:
    job = Recruitment(
        title=data.title,
        description=data.description,
        department=data.department,
        requirements=data.requirements,
        positions=data.positions,
        deadline=data.deadline,
        qualifications=data.qualifications,
        posted_by=posted_by,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info(f"Job posted: {job.title}")
    return job


def get_job_by_id(db: Session, job_id: int) -> Optional[Recruitment]:
    return db.query(Recruitment).filter(Recruitment.id == job_id).first()


def get_jobs(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Recruitment], int]:
    query = db.query(Recruitment)
    if status:
        query = query.filter(Recruitment.status == status)
    if department:
        query = query.filter(Recruitment.department == department)
    if search:
        query = query.filter(Recruitment.title.ilike(f"%{search}%"))
    total = query.count()
    jobs = query.order_by(Recruitment.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return jobs, total


def update_job(db: Session, job_id: int, data: RecruitmentUpdate) -> Optional[Recruitment]:
    job = get_job_by_id(db, job_id)
    if not job:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: int) -> bool:
    job = get_job_by_id(db, job_id)
    if not job:
        return False
    db.delete(job)
    db.commit()
    logger.info(f"Job deleted: {job.title}")
    return True


# ---- Applications ----

def submit_application(
    db: Session,
    recruitment_id: int,
    user_id: int,
    cover_letter: Optional[str] = None,
    cv_path: Optional[str] = None,
) -> Application | None:
    # Check if already applied
    existing = (
        db.query(Application)
        .filter(Application.recruitment_id == recruitment_id, Application.user_id == user_id)
        .first()
    )
    if existing:
        return None  # Already applied
    
    app = Application(
        recruitment_id=recruitment_id,
        user_id=user_id,
        cover_letter=cover_letter,
        cv_path=cv_path,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    logger.info(f"Application submitted: user {user_id} for job {recruitment_id}")
    return app


def get_applications_for_job(db: Session, job_id: int) -> list[Application]:
    return db.query(Application).filter(Application.recruitment_id == job_id).all()


def get_user_applications(db: Session, user_id: int) -> list[Application]:
    return db.query(Application).filter(Application.user_id == user_id).all()


def update_application_status(
    db: Session, app_id: int, data: ApplicationStatusUpdate
) -> Optional[Application]:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        return None
    application.status = data.status
    if data.reviewer_notes:
        application.reviewer_notes = data.reviewer_notes
    db.commit()
    db.refresh(application)
    return application
