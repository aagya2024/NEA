"""
Notice Routes
==============
Endpoints: GET /notices, GET /notices/{id}, POST /notices, PUT /notices/{id}, DELETE /notices/{id}
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.notice import NoticeCreate, NoticeUpdate, NoticeResponse, NoticeListResponse
from app.services import notice_service
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter(prefix="/api/notices", tags=["Notices"])


@router.get("", response_model=NoticeListResponse)
def list_notices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    active_only: bool = True,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List notices (active/non-expired by default)."""
    notices, total = notice_service.get_notices(db, page, per_page, active_only, type, priority, search)
    items = []
    for n in notices:
        resp = NoticeResponse.model_validate(n)
        resp.author_name = n.author.full_name if n.author else None
        items.append(resp)
    return NoticeListResponse(notices=items, total=total, page=page, per_page=per_page)


@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = notice_service.get_notice_by_id(db, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    resp = NoticeResponse.model_validate(notice)
    resp.author_name = notice.author.full_name if notice.author else None
    return resp


@router.post("", response_model=NoticeResponse, status_code=201)
def create_notice(
    data: NoticeCreate,
    current_user: User = Depends(require_permission("create_notice")),
    db: Session = Depends(get_db),
):
    notice = notice_service.create_notice(db, data, current_user.id)
    return NoticeResponse.model_validate(notice)


@router.put("/{notice_id}", response_model=NoticeResponse)
def update_notice(
    notice_id: int, data: NoticeUpdate,
    _=Depends(require_permission("edit_notice")),
    db: Session = Depends(get_db),
):
    notice = notice_service.update_notice(db, notice_id, data)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return NoticeResponse.model_validate(notice)


@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    _=Depends(require_permission("delete_notice")),
    db: Session = Depends(get_db),
):
    if not notice_service.delete_notice(db, notice_id):
        raise HTTPException(status_code=404, detail="Notice not found")
    return {"message": "Notice deleted"}
