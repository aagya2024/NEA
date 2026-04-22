"""
Form Routes
============
CRUD endpoints for downloadable form templates.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form as FormField
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.form import FormCreate, FormResponse, FormListResponse
from app.services import form_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/forms", tags=["Forms"])


@router.get("", response_model=FormListResponse)
def list_forms(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List form templates (paginated)."""
    return form_service.get_forms(db, page, per_page, category, search)


@router.post("", response_model=FormResponse, status_code=201)
async def upload_form(
    title: str = FormField(...),
    description: Optional[str] = FormField(None),
    category: str = FormField("Other"),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("upload_form")),
    db: Session = Depends(get_db),
):
    """Upload a new form template."""
    form_data = FormCreate(title=title, description=description, category=category)
    return await form_service.create_form(db, form_data, file, current_user)


@router.get("/{form_id}/download")
def download_form(
    form_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a form template file."""
    form = form_service.get_form_by_id(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    return FileResponse(
        path=form.file_path,
        filename=form.original_filename or "form",
        media_type="application/octet-stream",
    )


@router.delete("/{form_id}")
def delete_form(
    form_id: int,
    _=Depends(require_permission("delete_form")),
    db: Session = Depends(get_db),
):
    """Delete a form template."""
    form_service.delete_form(db, form_id)
    return {"message": "Form deleted successfully"}
