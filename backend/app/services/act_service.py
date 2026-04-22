"""
Act Service
============
CRUD operations for acts, bylaws, and regulations.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.act import Act
from app.schemas.act import ActCreate, ActUpdate
from app.utils.logger import logger


def create_act(
    db: Session,
    data: ActCreate,
    file_path: Optional[str] = None,
    original_filename: Optional[str] = None,
    uploaded_by: Optional[int] = None,
) -> Act:
    act = Act(
        title=data.title,
        content=data.content,
        type=data.type,
        tags=data.tags,
        year=data.year,
        file_path=file_path,
        original_filename=original_filename,
        uploaded_by=uploaded_by,
    )
    db.add(act)
    db.commit()
    db.refresh(act)
    logger.info(f"Act created: {act.title}")
    return act


def get_act_by_id(db: Session, act_id: int) -> Optional[Act]:
    return db.query(Act).filter(Act.id == act_id).first()


def get_acts(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    act_type: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
) -> tuple[list[Act], int]:
    query = db.query(Act)
    if act_type:
        query = query.filter(Act.type == act_type)
    if year:
        query = query.filter(Act.year == year)
    if search:
        query = query.filter(Act.title.ilike(f"%{search}%"))
    total = query.count()
    acts = query.order_by(Act.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return acts, total


def update_act(db: Session, act_id: int, data: ActUpdate) -> Optional[Act]:
    act = get_act_by_id(db, act_id)
    if not act:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(act, field, value)
    db.commit()
    db.refresh(act)
    return act


def delete_act(db: Session, act_id: int) -> bool:
    act = get_act_by_id(db, act_id)
    if not act:
        return False
    db.delete(act)
    db.commit()
    logger.info(f"Act deleted: {act.title}")
    return True
