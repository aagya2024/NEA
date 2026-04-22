"""
Document Routes
================
Endpoints: GET /documents, GET /documents/{id}, POST /documents,
           PUT /documents/{id}, DELETE /documents/{id}, GET /documents/{id}/download
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form as FastAPIForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse
from app.services import document_service
from app.utils.security import get_current_user
from app.utils.file_handler import save_upload, get_file_path
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs, total = document_service.get_documents(db, page, per_page, category, search)
    items = []
    for d in docs:
        resp = DocumentResponse.model_validate(d)
        resp.uploader_name = d.uploaded_by_user.full_name if d.uploaded_by_user else None
        items.append(resp)
    return DocumentListResponse(documents=items, total=total, page=page, per_page=per_page)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    resp = DocumentResponse.model_validate(doc)
    resp.uploader_name = doc.uploaded_by_user.full_name if doc.uploaded_by_user else None
    return resp


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    title: str = FastAPIForm(...),
    description: Optional[str] = FastAPIForm(None),
    category: str = FastAPIForm("Other"),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("upload_document")),
    db: Session = Depends(get_db),
):
    file_path = await save_upload(file, subfolder="documents", allowed_categories=["document"])
    data = DocumentCreate(title=title, description=description, category=category)
    doc = document_service.create_document(
        db, data, file_path, file.filename or "unknown",
        file.size or 0, file.content_type or "application/octet-stream",
        current_user.id,
    )
    return DocumentResponse.model_validate(doc)


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int, data: DocumentUpdate,
    _=Depends(require_permission("edit_document")),
    db: Session = Depends(get_db),
):
    doc = document_service.update_document(db, doc_id, data)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    _=Depends(require_permission("delete_document")),
    db: Session = Depends(get_db),
):
    if not document_service.delete_document(db, doc_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted"}


@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    document_service.increment_download_count(db, doc_id)
    file_path = get_file_path(doc.file_path)
    return FileResponse(
        path=str(file_path),
        filename=doc.original_filename or "download",
        media_type=doc.mime_type or "application/octet-stream",
    )
