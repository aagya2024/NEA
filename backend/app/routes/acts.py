"""
Act Routes
===========
Endpoints: GET /acts, GET /acts/{id}, POST /acts, PUT /acts/{id}, DELETE /acts/{id}
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form as FastAPIForm
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.act import ActCreate, ActUpdate, ActResponse, ActListResponse
from app.services import act_service
from app.utils.security import get_current_user
from app.utils.file_handler import save_upload
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter(prefix="/api/acts", tags=["Acts & Bylaws"])


@router.get("", response_model=ActListResponse)
def list_acts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    acts, total = act_service.get_acts(db, page, per_page, type, year, search)
    return ActListResponse(
        acts=[ActResponse.model_validate(a) for a in acts],
        total=total, page=page, per_page=per_page,
    )


@router.get("/{act_id}", response_model=ActResponse)
def get_act(act_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    act = act_service.get_act_by_id(db, act_id)
    if not act:
        raise HTTPException(status_code=404, detail="Act not found")
    return ActResponse.model_validate(act)


@router.post("", response_model=ActResponse, status_code=201)
async def create_act(
    title: str = FastAPIForm(...),
    content: Optional[str] = FastAPIForm(None),
    type: str = FastAPIForm("Act"),
    year: Optional[int] = FastAPIForm(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_permission("manage_acts")),
    db: Session = Depends(get_db),
):
    file_path = None
    original_filename = None
    if file and file.filename:
        file_path = await save_upload(file, subfolder="acts", allowed_categories=["document"])
        original_filename = file.filename

    data = ActCreate(title=title, content=content, type=type, year=year)
    act = act_service.create_act(db, data, file_path, original_filename, current_user.id)
    return ActResponse.model_validate(act)


@router.put("/{act_id}", response_model=ActResponse)
def update_act(
    act_id: int, data: ActUpdate,
    _=Depends(require_permission("manage_acts")),
    db: Session = Depends(get_db),
):
    act = act_service.update_act(db, act_id, data)
    if not act:
        raise HTTPException(status_code=404, detail="Act not found")
    return ActResponse.model_validate(act)


@router.delete("/{act_id}")
def delete_act(
    act_id: int,
    _=Depends(require_permission("manage_acts")),
    db: Session = Depends(get_db),
):
    if not act_service.delete_act(db, act_id):
        raise HTTPException(status_code=404, detail="Act not found")
    return {"message": "Act deleted"}
