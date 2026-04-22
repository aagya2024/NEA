"""
Role Routes
============
Endpoints: GET /roles, POST /roles, PUT /roles/{id}, DELETE /roles/{id},
           GET /permissions, PUT /roles/{id}/permissions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, PermissionResponse, AssignPermissions
from app.services import role_service
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/roles", tags=["Roles & Permissions"])


@router.get("", response_model=list[RoleResponse])
def list_roles(
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """List all roles with their permissions."""
    roles = role_service.get_all_roles(db)
    result = []
    for role in roles:
        perms = role_service.get_role_permissions(db, role.id)
        result.append(RoleResponse(
            id=role.id, name=role.name, description=role.description,
            is_system_role=role.is_system_role, created_at=role.created_at,
            permissions=[PermissionResponse.model_validate(p) for p in perms],
        ))
    return result


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    data: RoleCreate,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Create a new custom role."""
    existing = role_service.get_role_by_name(db, data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    role = role_service.create_role(db, data)
    return RoleResponse(
        id=role.id, name=role.name, description=role.description,
        is_system_role=role.is_system_role, created_at=role.created_at,
    )


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int, data: RoleUpdate,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Update a role."""
    role = role_service.update_role(db, role_id, data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleResponse(
        id=role.id, name=role.name, description=role.description,
        is_system_role=role.is_system_role, created_at=role.created_at,
    )


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Delete a custom role (cannot delete system roles)."""
    if not role_service.delete_role(db, role_id):
        raise HTTPException(status_code=400, detail="Cannot delete this role (system role or not found)")
    return {"message": "Role deleted"}


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """List all available permissions."""
    return [PermissionResponse.model_validate(p) for p in role_service.get_all_permissions(db)]


@router.put("/{role_id}/permissions")
def assign_role_permissions(
    role_id: int, data: AssignPermissions,
    _=Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db),
):
    """Replace all permissions for a role."""
    if not role_service.assign_permissions(db, role_id, data.permission_ids):
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Permissions updated"}
