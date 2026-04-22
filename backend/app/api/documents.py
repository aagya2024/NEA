"""
Document Routes
================
CRUD endpoints for document management with file upload/download.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse
from app.services import document_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission

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
    """List documents (paginated)."""
    return document_service.get_documents(db, page, per_page, category, search)


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category: str = Form("Other"),
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("upload_document")),
    db: Session = Depends(get_db),
):
    """Upload a new document."""
    doc_data = DocumentCreate(title=title, description=description, category=category)
    return await document_service.create_document(db, doc_data, file, current_user)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get document metadata."""
    doc = document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download a document file."""
    doc = document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document_service.increment_download_count(db, doc_id)
    
    return FileResponse(
        path=doc.file_path,
        filename=doc.original_filename or "document",
        media_type=doc.mime_type or "application/octet-stream",
    )


@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int,
    doc_data: DocumentUpdate,
    _=Depends(require_permission("edit_document")),
    db: Session = Depends(get_db),
):
    """Update document metadata."""
    return document_service.update_document(db, doc_id, doc_data)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    _=Depends(require_permission("delete_document")),
    db: Session = Depends(get_db),
):
    """Delete a document."""
    document_service.delete_document(db, doc_id)
    return {"message": "Document deleted successfully"}
