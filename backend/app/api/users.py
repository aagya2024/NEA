"""
User Management Routes
=======================
CRUD endpoints for managing users (admin operations).
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserUpdate, UserProfileUpdate, ChangePassword,
    UserResponse, UserListResponse,
)
from app.services import user_service
from app.utils.security import get_current_user, hash_password, verify_password
from app.middleware.rbac import require_permission
from fastapi import HTTPException, status

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    _=Depends(require_permission("view_users")),
    db: Session = Depends(get_db),
):
    """List all users (paginated) with optional filters."""
    return user_service.get_users(db, page, per_page, search, role_id, is_active)


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    _=Depends(require_permission("create_user")),
    db: Session = Depends(get_db),
):
    """Create a new user account."""
    return user_service.create_user(db, user_data)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    _=Depends(require_permission("view_users")),
    db: Session = Depends(get_db),
):
    """Get a specific user by ID."""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    _=Depends(require_permission("edit_user")),
    db: Session = Depends(get_db),
):
    """Update a user's information."""
    return user_service.update_user(db, user_id, user_data)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    _=Depends(require_permission("delete_user")),
    db: Session = Depends(get_db),
):
    """Delete a user account."""
    user_service.delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@router.put("/me/profile", response_model=UserResponse)
def update_own_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's own profile."""
    return user_service.update_profile(db, current_user, profile_data)


@router.post("/me/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password."""
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
