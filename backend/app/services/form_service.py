"""
Form Service
=============
CRUD operations for downloadable form templates.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.form import Form
from app.schemas.form import FormCreate, FormUpdate
from app.utils.logger import logger


def create_form(
    db: Session,
    data: FormCreate,
    file_path: str,
    original_filename: str,
    uploaded_by: int,
) -> Form:
    form = Form(
        title=data.title,
        description=data.description,
        category=data.category,
        file_path=file_path,
        original_filename=original_filename,
        uploaded_by=uploaded_by,
    )
    db.add(form)
    db.commit()
    db.refresh(form)
    logger.info(f"Form created: {form.title}")
    return form


def get_form_by_id(db: Session, form_id: int) -> Optional[Form]:
    return db.query(Form).filter(Form.id == form_id).first()


def get_forms(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Form], int]:
    query = db.query(Form)
    if category:
        query = query.filter(Form.category == category)
    if search:
        query = query.filter(Form.title.ilike(f"%{search}%"))
    total = query.count()
    forms = query.order_by(Form.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return forms, total


def update_form(db: Session, form_id: int, data: FormUpdate) -> Optional[Form]:
    form = get_form_by_id(db, form_id)
    if not form:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(form, field, value)
    db.commit()
    db.refresh(form)
    return form


def delete_form(db: Session, form_id: int) -> bool:
    form = get_form_by_id(db, form_id)
    if not form:
        return False
    db.delete(form)
    db.commit()
    logger.info(f"Form deleted: {form.title}")
    return True


def increment_download_count(db: Session, form_id: int):
    form = get_form_by_id(db, form_id)
    if form:
        form.download_count = (form.download_count or 0) + 1
        db.commit()
