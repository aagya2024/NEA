"""
System Routes
==============
Endpoints for system configuration and audit logs.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.system_config import SystemConfig
from app.models.log import AuditLog
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/config")
def get_system_config(
    _=Depends(require_permission("system_config")),
    db: Session = Depends(get_db),
):
    """Get all system configuration settings."""
    configs = db.query(SystemConfig).all()
    return {c.key: {"value": c.value, "description": c.description} for c in configs}


@router.put("/config")
def update_system_config(
    updates: dict,
    current_user: User = Depends(require_permission("system_config")),
    db: Session = Depends(get_db),
):
    """Update system configuration settings."""
    for key, value in updates.items():
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = str(value)
            config.updated_by = current_user.id
        else:
            config = SystemConfig(
                key=key,
                value=str(value),
                updated_by=current_user.id,
            )
            db.add(config)
    
    db.commit()
    return {"message": "Configuration updated successfully"}


@router.get("/logs")
def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    _=Depends(require_permission("system_config")),
    db: Session = Depends(get_db),
):
    """View audit logs (paginated)."""
    query = db.query(AuditLog)
    
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    total = query.count()
    logs = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": str(log.created_at) if log.created_at else None,
            }
            for log in logs
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/health")
def health_check():
    """Public health check endpoint (no auth required)."""
    return {"status": "healthy", "service": "NEA Intranet Portal"}
