"""
Form Routes
============
Endpoints: GET /forms, GET /forms/{id}, POST /forms, PUT /forms/{id},
           DELETE /forms/{id}, GET /forms/{id}/download
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form as FastAPIForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.form import FormCreate, FormUpdate, FormResponse, FormListResponse
from app.services import form_service
from app.utils.security import get_current_user
from app.utils.file_handler import save_upload, get_file_path
from app.middleware.rbac import require_permission
from app.models.user import User

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
    forms, total = form_service.get_forms(db, page, per_page, category, search)
    items = []
    for f in forms:
        resp = FormResponse.model_validate(f)
        resp.uploader_name = f.uploaded_by_user.full_name if f.uploaded_by_user else None
        items.append(resp)
    return FormListResponse(forms=items, total=total, page=page, per_page=per_page)


@router.get("/{form_id}", response_model=FormResponse)
def get_form(form_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    form = form_service.get_form_by_id(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    resp = FormResponse.model_validate(form)
    resp.uploader_name = form.uploaded_by_user.full_name if form.uploaded_by_user else None
    return resp


@router.post("", response_model=FormResponse, status_code=201)
async def upload_form(
    title: str = FastAPIForm(...),
    description: Optional[str] = FastAPIForm(None),
    category: str = FastAPIForm("Other"),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("upload_form")),
    db: Session = Depends(get_db),
):
    file_path = await save_upload(file, subfolder="forms", allowed_categories=["document"])
    data = FormCreate(title=title, description=description, category=category)
    form = form_service.create_form(db, data, file_path, file.filename or "unknown", current_user.id)
    return FormResponse.model_validate(form)


@router.put("/{form_id}", response_model=FormResponse)
def update_form(
    form_id: int, data: FormUpdate,
    _=Depends(require_permission("edit_form")),
    db: Session = Depends(get_db),
):
    form = form_service.update_form(db, form_id, data)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return FormResponse.model_validate(form)


@router.delete("/{form_id}")
def delete_form(
    form_id: int,
    _=Depends(require_permission("delete_form")),
    db: Session = Depends(get_db),
):
    if not form_service.delete_form(db, form_id):
        raise HTTPException(status_code=404, detail="Form not found")
    return {"message": "Form deleted"}


@router.get("/{form_id}/download")
def download_form(
    form_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = form_service.get_form_by_id(db, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    form_service.increment_download_count(db, form_id)
    file_path = get_file_path(form.file_path)
    return FileResponse(path=str(file_path), filename=form.original_filename or "download")
