"""
Permission & RolePermission Models
====================================
These two models work together to create a DYNAMIC permission system.

HOW DYNAMIC RBAC WORKS:
1. 'permissions' table stores ALL possible actions (e.g., create_news, delete_form)
2. 'role_permissions' table links roles to their allowed permissions
3. When a user tries to do something, we check:
   - What role does the user have?
   - Does that role have the required permission?

This is DYNAMIC because:
- Super Admin can change which permissions each role has
- No permissions are hardcoded in the application code
- New permissions can be added without changing code

EXAMPLE:
- Permission: "create_news" (key) / "Create News Articles" (name)
- Role: "Admin"
- RolePermission: links Admin -> create_news
- Result: Users with Admin role can create news articles
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Permission(Base):
    """
    Database table: 'permissions'
    
    Each row represents one action that can be performed in the system.
    The 'key' is used in code to check permissions (e.g., "create_news").
    The 'name' is a human-readable label (e.g., "Create News Articles").
    """
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Unique key used in code (e.g., "create_news", "manage_roles")
    # This is what we check in the RBAC middleware
    key = Column(String(100), unique=True, nullable=False, index=True)
    
    # Human-readable name (e.g., "Create News Articles")
    name = Column(String(200), nullable=False)
    
    # Description of what this permission allows
    description = Column(Text, nullable=True)
    
    # Module this permission belongs to (e.g., "news", "recruitment", "system")
    # Useful for grouping permissions in the admin UI
    module = Column(String(100), nullable=False, default="general")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to role_permissions
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Permission(key='{self.key}', module='{self.module}')>"


class RolePermission(Base):
    """
    Database table: 'role_permissions'
    
    This is a "many-to-many" junction table that links roles to permissions.
    
    For example:
    - role_id=2 (Admin), permission_id=1 (create_news)
      -> Admin can create news
    - role_id=3 (HR), permission_id=5 (create_job)
      -> HR can create jobs
    """
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to the roles table
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    
    # Foreign key to the permissions table
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ---- Relationships ----
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    # Ensure a role can't have the same permission twice
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
