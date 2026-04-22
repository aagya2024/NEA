"""
Document Service
=================
CRUD operations for document management with file handling.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.utils.logger import logger


def create_document(
    db: Session,
    data: DocumentCreate,
    file_path: str,
    original_filename: str,
    file_size: int,
    mime_type: str,
    uploaded_by: int,
) -> Document:
    doc = Document(
        title=data.title,
        description=data.description,
        category=data.category,
        file_path=file_path,
        original_filename=original_filename,
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=uploaded_by,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info(f"Document created: {doc.title}")
    return doc


def get_document_by_id(db: Session, doc_id: int) -> Optional[Document]:
    return db.query(Document).filter(Document.id == doc_id).first()


def get_documents(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Document], int]:
    query = db.query(Document)

    if category:
        query = query.filter(Document.category == category)
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))

    total = query.count()
    docs = query.order_by(Document.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return docs, total


def update_document(db: Session, doc_id: int, data: DocumentUpdate) -> Optional[Document]:
    doc = get_document_by_id(db, doc_id)
    if not doc:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)

    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc_id: int) -> bool:
    doc = get_document_by_id(db, doc_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    logger.info(f"Document deleted: {doc.title}")
    return True


def increment_download_count(db: Session, doc_id: int):
    doc = get_document_by_id(db, doc_id)
    if doc:
        doc.download_count = (doc.download_count or 0) + 1
        db.commit()
