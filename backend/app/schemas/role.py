"""
Role & Permission Schemas
==========================
Request/response schemas for role and permission management.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PermissionResponse(BaseModel):
    """Schema for a single permission."""
    id: int
    key: str
    name: str
    description: Optional[str] = None
    module: str

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Schema for creating a new role."""
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(BaseModel):
    """Schema for role data in responses."""
    id: int
    name: str
    description: Optional[str] = None
    is_system_role: bool
    created_at: Optional[datetime] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class AssignPermissions(BaseModel):
    """Schema for assigning permissions to a role."""
    permission_ids: List[int]
