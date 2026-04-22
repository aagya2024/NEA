"""
RBAC Middleware
================
Permission-checking dependency for FastAPI routes.

USAGE:
    @router.post("/news", dependencies=[Depends(require_permission("create_news"))])
    def create_news_article(...):
        ...

HOW IT WORKS:
1. Extracts the current user from the JWT token
2. Looks up the user's role permissions in the database
3. Checks if the required permission key exists
4. Raises 403 Forbidden if not
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.models.permission import Permission, RolePermission


def require_permission(permission_key: str):
    """
    Creates a FastAPI dependency that checks if the current user
    has the specified permission.
    
    Args:
        permission_key: The permission key to check (e.g., "create_news")
    
    Returns:
        A dependency function for use with Depends()
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        # Check if user's role has the required permission
        has_perm = (
            db.query(RolePermission)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .filter(
                RolePermission.role_id == current_user.role_id,
                Permission.key == permission_key,
            )
            .first()
        )
        
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission_key}",
            )
        
        return current_user
    
    return permission_checker
