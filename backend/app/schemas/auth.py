"""
Authentication Schemas
=======================
Request/response schemas for login, token refresh, and auth responses.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List


class LoginRequest(BaseModel):
    """Login with email and password."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response containing JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token."""
    refresh_token: str


class UserProfile(BaseModel):
    """Current user profile response (used by /auth/me)."""
    id: int
    email: str
    full_name: str
    department: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role_id: int
    role_name: str
    permissions: List[str] = []
    is_active: bool

    class Config:
        from_attributes = True
