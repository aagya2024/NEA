"""
Auth Service
=============
Handles login, token creation, and password verification.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.models.role import Role
from app.models.permission import RolePermission, Permission
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
)
from app.utils.logger import logger


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Verify email/password and return the user if valid."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.warning(f"Login attempt for non-existent email: {email}")
        return None
    if not verify_password(password, user.password_hash):
        logger.warning(f"Invalid password for user: {email}")
        return None
    if not user.is_active:
        logger.warning(f"Login attempt for deactivated user: {email}")
        return None
    return user


def create_tokens(user: User) -> dict:
    """Create access and refresh tokens for a user."""
    token_data = {"sub": str(user.id), "email": user.email, "role_id": str(user.role_id)}
    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict | None:
    """Validate a refresh token and issue new tokens."""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            return None
        return create_tokens(user)
    except Exception:
        return None


def update_last_login(db: Session, user: User):
    """Update the user's last_login timestamp."""
    user.last_login = datetime.now(timezone.utc)
    db.commit()


def get_user_permissions(db: Session, role_id: int) -> list[str]:
    """Get all permission keys for a given role."""
    perms = (
        db.query(Permission.key)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role_id == role_id)
        .all()
    )
    return [p.key for p in perms]
