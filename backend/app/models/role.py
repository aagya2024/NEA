"""
Role Model
==========
Stores the different user roles in the system.

ROLES IN THIS SYSTEM:
- Super Admin: Full system access, can manage everything
- Admin: Can publish content, manage users (except Super Admin)
- HR: Can manage recruitment and HR-related content
- Employee: Can view content, apply for jobs, use chatbot
- Viewer: Limited read-only access

The 'is_system_role' flag marks roles that cannot be deleted
(like Super Admin). Custom roles can be created by Super Admin.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    """
    Database table: 'roles'
    
    Each role defines a set of permissions that users with
    that role can perform. Permissions are linked through
    the role_permissions table.
    """
    __tablename__ = "roles"
    
    # Primary key - auto-incrementing unique ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Role name (e.g., "Super Admin", "Employee")
    # Must be unique - can't have two roles with the same name
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    # Description of what this role can do
    description = Column(Text, nullable=True)
    
    # System roles can't be deleted (Super Admin, Admin, etc.)
    is_system_role = Column(Boolean, default=False)
    
    # When this role was created
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # When this role was last updated  
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # ---- Relationships ----
    # A role has many users
    users = relationship("User", back_populates="role")
    
    # A role has many permission mappings
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
