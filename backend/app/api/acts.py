"""
Acts & Bylaws Routes
=====================
CRUD endpoints for acts, bylaws, regulations, and directives.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.act import ActCreate, ActUpdate, ActResponse, ActListResponse
from app.services import act_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/acts", tags=["Acts & Bylaws"])


@router.get("", response_model=ActListResponse)
def list_acts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    act_type: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List acts and bylaws (paginated)."""
    return act_service.get_acts(db, page, per_page, act_type, year, search)


@router.get("/{act_id}", response_model=ActResponse)
def get_act(
    act_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single act."""
    act = act_service.get_act_by_id(db, act_id)
    if not act:
        raise HTTPException(status_code=404, detail="Act not found")
    return act


@router.post("", response_model=ActResponse, status_code=201)
async def create_act(
    title: str = Form(...),
    content: Optional[str] = Form(None),
    act_type: str = Form("Act"),
    year: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_permission("create_act")),
    db: Session = Depends(get_db),
):
    """Create a new act entry with optional file upload."""
    act_data = ActCreate(title=title, content=content, type=act_type, year=year)
    return await act_service.create_act(db, act_data, file, current_user.id)


@router.put("/{act_id}", response_model=ActResponse)
def update_act(
    act_id: int,
    act_data: ActUpdate,
    _=Depends(require_permission("edit_act")),
    db: Session = Depends(get_db),
):
    """Update an act."""
    return act_service.update_act(db, act_id, act_data)


@router.delete("/{act_id}")
def delete_act(
    act_id: int,
    _=Depends(require_permission("delete_act")),
    db: Session = Depends(get_db),
):
    """Delete an act."""
    act_service.delete_act(db, act_id)
    return {"message": "Act deleted successfully"}


@router.get("/{act_id}/download")
def download_act(
    act_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download an act's PDF file."""
    act = act_service.get_act_by_id(db, act_id)
    if not act or not act.file_path:
        raise HTTPException(status_code=404, detail="Act file not found")
    
    return FileResponse(
        path=act.file_path,
        filename=act.original_filename or "act.pdf",
        media_type="application/pdf",
    )
