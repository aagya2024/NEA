"""
User Schemas
=============
Request/response schemas for user management.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    full_name: str
    password: str
    department: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    role_id: int


class UserUpdate(BaseModel):
    """Schema for updating an existing user (all fields optional)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    """Schema for a user updating their own profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None


class ChangePassword(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: int
    email: str
    full_name: str
    department: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role_id: int
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list response."""
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
