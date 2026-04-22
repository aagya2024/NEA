"""
Notice Routes
==============
CRUD endpoints for notices/announcements.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse, NoticeListResponse
from app.services import notice_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/notices", tags=["Notices"])


@router.get("", response_model=NoticeListResponse)
def list_notices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    notice_type: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List notices (paginated)."""
    return notice_service.get_notices(db, page, per_page, notice_type, priority, active_only=True)


@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single notice."""
    notice = notice_service.get_notice_by_id(db, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    result = NoticeResponse.model_validate(notice)
    if notice.author:
        result.author_name = notice.author.full_name
    return result


@router.post("", response_model=NoticeResponse, status_code=201)
def create_notice(
    notice_data: NoticeCreate,
    current_user: User = Depends(require_permission("create_notice")),
    db: Session = Depends(get_db),
):
    """Create a new notice."""
    return notice_service.create_notice(db, notice_data, current_user)


@router.put("/{notice_id}", response_model=NoticeResponse)
def update_notice(
    notice_id: int,
    notice_data: NoticeUpdate,
    _=Depends(require_permission("edit_notice")),
    db: Session = Depends(get_db),
):
    """Update a notice."""
    return notice_service.update_notice(db, notice_id, notice_data)


@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    _=Depends(require_permission("delete_notice")),
    db: Session = Depends(get_db),
):
    """Delete a notice."""
    notice_service.delete_notice(db, notice_id)
    return {"message": "Notice deleted successfully"}
