"""
System Routes
==============
Endpoints: GET /system/config, PUT /system/config, GET /system/logs
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.system_config import SystemConfig
from app.models.log import AuditLog
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/system", tags=["System"])


class ConfigUpdate(BaseModel):
    key: str
    value: str


@router.get("/config")
def get_system_config(
    _=Depends(require_permission("manage_system")),
    db: Session = Depends(get_db),
):
    """Get all system configuration key-value pairs."""
    configs = db.query(SystemConfig).all()
    return {c.key: c.value for c in configs}


@router.put("/config")
def update_config(
    data: ConfigUpdate,
    _=Depends(require_permission("manage_system")),
    db: Session = Depends(get_db),
):
    """Update or create a system configuration value."""
    config = db.query(SystemConfig).filter(SystemConfig.key == data.key).first()
    if config:
        config.value = data.value
    else:
        config = SystemConfig(key=data.key, value=data.value)
        db.add(config)
    db.commit()
    return {"message": f"Config '{data.key}' updated"}


@router.get("/logs")
def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    _=Depends(require_permission("view_logs")),
    db: Session = Depends(get_db),
):
    """Get audit logs with optional filters."""
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": str(log.created_at),
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }
