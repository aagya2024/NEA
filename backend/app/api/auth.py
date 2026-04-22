"""
Authentication Routes
======================
Handles login, token refresh, logout, and current user profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, UserProfile
from app.services.auth_service import authenticate_user, create_tokens, refresh_access_token, get_user_permissions
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password, receive JWT tokens.
    
    Returns access_token (short-lived) and refresh_token (long-lived).
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Get a new access token using a valid refresh token."""
    tokens = refresh_access_token(db, refresh_data.refresh_token)
    
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
    """Get the current authenticated user's profile with permissions."""
    permissions = get_user_permissions(db, current_user)
    
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


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout the current user.
    
    Note: With JWT, true server-side invalidation requires a token blacklist
    (Redis). For now, the client discards the token.
    """
    return {"message": "Successfully logged out"}
