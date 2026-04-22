"""
Security Utilities
==================
JWT token creation/verification and password hashing using bcrypt.

USAGE:
    from app.utils.security import (
        hash_password, verify_password,
        create_access_token, create_refresh_token,
        get_current_user
    )

HOW JWT WORKS:
1. User logs in with email + password
2. Server creates an access token (short-lived) and refresh token (long-lived)
3. Client sends the access token in the "Authorization: Bearer <token>" header
4. Server verifies the token and extracts the user info
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

# ---- Password Hashing ----
# CryptContext handles hashing and verifying passwords
# 'bcrypt' is the recommended algorithm for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- OAuth2 Scheme ----
# This tells FastAPI where to look for the JWT token
# tokenUrl is the endpoint where clients get their token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Example:
        hashed = hash_password("my_password")
        # hashed = "$2b$12$..."  (60 characters)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain-text password matches a hashed password.
    
    Example:
        is_valid = verify_password("my_password", hashed)
        # is_valid = True or False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a short-lived JWT access token.
    
    Args:
        data: Dictionary with claims to encode (must include "sub" for user ID)
        expires_delta: Custom expiration time (defaults to settings value)
    
    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived JWT refresh token.
    
    Refresh tokens are used to get new access tokens without re-entering
    the password. They last longer (e.g., 7 days vs 30 minutes).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    
    Raises JWTError if the token is invalid or expired.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency that extracts the current user from the JWT token.
    
    Usage in API routes:
        @router.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None:
            raise credentials_exception
        if token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Import here to avoid circular imports
    from app.models.user import User
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    
    return user
