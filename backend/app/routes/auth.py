"""
Auth Routes
============
Endpoints: POST /login, POST /refresh, GET /me
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserProfile
from app.services import auth_service
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = auth_service.authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    auth_service.update_last_login(db, user)
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Get new tokens using a refresh token."""
    tokens = auth_service.refresh_access_token(db, data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return tokens


@router.get("/me", response_model=UserProfile)
def get_current_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's profile with role and permissions."""
    permissions = auth_service.get_user_permissions(db, current_user.role_id)
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        department=current_user.department,
        employee_id=current_user.employee_id,
        phone=current_user.phone,
        avatar=current_user.avatar,
        role_id=current_user.role_id,
        role_name=current_user.role.name if current_user.role else "Unknown",
        permissions=permissions,
        is_active=current_user.is_active,
    )
