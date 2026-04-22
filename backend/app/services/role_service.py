"""
Role Service
=============
CRUD operations for roles and permission assignment.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.schemas.role import RoleCreate, RoleUpdate
from app.utils.logger import logger


def create_role(db: Session, data: RoleCreate) -> Role:
    """Create a new custom role."""
    role = Role(name=data.name, description=data.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    logger.info(f"Role created: {role.name}")
    return role


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()


def get_all_roles(db: Session) -> list[Role]:
    return db.query(Role).all()


def update_role(db: Session, role_id: int, data: RoleUpdate) -> Optional[Role]:
    role = get_role_by_id(db, role_id)
    if not role:
        return None
    if role.is_system_role:
        # Only allow description updates on system roles
        if data.description is not None:
            role.description = data.description
    else:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(role, field, value)
    db.commit()
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: int) -> bool:
    role = get_role_by_id(db, role_id)
    if not role or role.is_system_role:
        return False
    db.delete(role)
    db.commit()
    logger.info(f"Role deleted: {role.name}")
    return True


def get_all_permissions(db: Session) -> list[Permission]:
    return db.query(Permission).order_by(Permission.module, Permission.key).all()


def get_role_permissions(db: Session, role_id: int) -> list[Permission]:
    return (
        db.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == role_id)
        .all()
    )


def assign_permissions(db: Session, role_id: int, permission_ids: list[int]) -> bool:
    """Replace all permissions for a role with the given list."""
    role = get_role_by_id(db, role_id)
    if not role:
        return False

    # Remove existing permissions
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()

    # Add new permissions
    for pid in permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=pid))

    db.commit()
    logger.info(f"Permissions updated for role: {role.name}")
    return True
