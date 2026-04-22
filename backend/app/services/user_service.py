"""
User Service
=============
CRUD operations for user management.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.utils.security import hash_password, verify_password
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate
from app.utils.logger import logger


def create_user(db: Session, data: UserCreate) -> User:
    """Create a new user account."""
    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        department=data.department,
        employee_id=data.employee_id,
        phone=data.phone,
        role_id=data.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"User created: {user.email}")
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Fetch a single user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetch a single user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> tuple[list[User], int]:
    """Get paginated list of users with optional filters."""
    query = db.query(User)

    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.employee_id.ilike(f"%{search}%"),
            )
        )
    if role_id is not None:
        query = query.filter(User.role_id == role_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return users, total


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    """Update user fields (admin operation)."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info(f"User updated: {user.email}")
    return user


def update_profile(db: Session, user: User, data: UserProfileUpdate) -> User:
    """Update a user's own profile (limited fields)."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """Change a user's password after verifying the current one."""
    if not verify_password(current_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    db.commit()
    return True


def delete_user(db: Session, user_id: int) -> bool:
    """Soft-delete (deactivate) a user."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    user.is_active = False
    db.commit()
    logger.info(f"User deactivated: {user.email}")
    return True
