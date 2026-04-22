"""
Notice Service
===============
CRUD operations for notices/announcements with expiry support.
"""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeUpdate
from app.utils.logger import logger


def create_notice(db: Session, data: NoticeCreate, author_id: int) -> Notice:
    notice = Notice(
        title=data.title,
        content=data.content,
        type=data.type,
        priority=data.priority,
        expires_at=data.expires_at,
        author_id=author_id,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    logger.info(f"Notice created: {notice.title}")
    return notice


def get_notice_by_id(db: Session, notice_id: int) -> Optional[Notice]:
    return db.query(Notice).filter(Notice.id == notice_id).first()


def get_notices(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    active_only: bool = False,
    notice_type: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Notice], int]:
    query = db.query(Notice)

    if active_only:
        now = datetime.now(timezone.utc)
        query = query.filter(
            (Notice.expires_at == None) | (Notice.expires_at > now)
        )
    if notice_type:
        query = query.filter(Notice.type == notice_type)
    if priority:
        query = query.filter(Notice.priority == priority)
    if search:
        query = query.filter(Notice.title.ilike(f"%{search}%"))

    total = query.count()
    notices = query.order_by(Notice.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return notices, total


def update_notice(db: Session, notice_id: int, data: NoticeUpdate) -> Optional[Notice]:
    notice = get_notice_by_id(db, notice_id)
    if not notice:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notice, field, value)

    db.commit()
    db.refresh(notice)
    return notice


def delete_notice(db: Session, notice_id: int) -> bool:
    notice = get_notice_by_id(db, notice_id)
    if not notice:
        return False
    db.delete(notice)
    db.commit()
    logger.info(f"Notice deleted: {notice.title}")
    return True
