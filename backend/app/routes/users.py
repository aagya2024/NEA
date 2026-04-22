"""
User Routes
============
Endpoints: GET /users, GET /users/{id}, POST /users, PUT /users/{id},
           DELETE /users/{id}, PUT /users/profile, PUT /users/password
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserProfileUpdate, ChangePassword,
    UserResponse, UserListResponse,
)
from app.services import user_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db),
):
    """List all users with pagination and filters."""
    users, total = user_service.get_users(db, page, per_page, search, role_id, is_active)
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total, page=page, per_page=per_page,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db),
):
    """Get a specific user by ID."""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    current_user: User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db),
):
    """Create a new user account."""
    existing = user_service.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db, data)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db),
):
    """Update a user (admin operation)."""
    user = user_service.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db),
):
    """Deactivate a user account."""
    if not user_service.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated"}


@router.put("/profile/me", response_model=UserResponse)
def update_my_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's own profile."""
    return user_service.update_profile(db, current_user, data)


@router.put("/password/change")
def change_my_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    if not user_service.change_password(db, current_user, data.current_password, data.new_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    return {"message": "Password changed successfully"}
