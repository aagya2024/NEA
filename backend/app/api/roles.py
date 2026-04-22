"""
Role & Permission Routes
=========================
CRUD endpoints for role management and permission assignment.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, PermissionResponse, AssignPermissions,
)
from app.services import role_service
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/roles", tags=["Roles & Permissions"])


@router.get("", response_model=list[RoleResponse])
def list_roles(
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """List all roles with their permissions."""
    roles = role_service.get_roles(db)
    result = []
    for role in roles:
        perms = role_service.get_role_permissions(db, role.id)
        role_resp = RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            created_at=role.created_at,
            permissions=[PermissionResponse.model_validate(p) for p in perms],
        )
        result.append(role_resp)
    return result


@router.post("", response_model=RoleResponse, status_code=201)
def create_role(
    role_data: RoleCreate,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Create a new custom role."""
    return role_service.create_role(db, role_data)


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Update a role."""
    return role_service.update_role(db, role_id, role_data)


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Delete a non-system role."""
    role_service.delete_role(db, role_id)
    return {"message": "Role deleted successfully"}


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """List all available permissions."""
    return role_service.get_all_permissions(db)


@router.put("/{role_id}/permissions")
def assign_permissions(
    role_id: int,
    data: AssignPermissions,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Assign permissions to a role (replaces existing permissions)."""
    role_service.assign_permissions(db, role_id, data.permission_ids)
    return {"message": "Permissions updated successfully"}
