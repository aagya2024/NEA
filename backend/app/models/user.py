"""
User Model
==========
Stores all users of the NEA Intranet system.

Each user belongs to exactly one role (Super Admin, Admin, HR, Employee, or Viewer).
The password is NEVER stored in plain text - it's always hashed using bcrypt.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    Database table: 'users'
    
    This stores employee accounts for the NEA intranet.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Email serves as the login username (must be unique)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Full name of the employee
    full_name = Column(String(255), nullable=False)
    
    # Hashed password (never store plain text!)
    password_hash = Column(String(255), nullable=False)
    
    # Which department they belong to (e.g., "Engineering", "Finance")
    department = Column(String(100), nullable=True)
    
    # Employee ID number (optional, for HR purposes)
    employee_id = Column(String(50), nullable=True, unique=True)
    
    # Phone number
    phone = Column(String(20), nullable=True)
    
    # Profile picture path
    avatar = Column(String(500), nullable=True)
    
    # Foreign key linking to the roles table
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Is this account active? (Inactive accounts can't log in)
    is_active = Column(Boolean, default=True)
    
    # Timestamp tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # ---- Relationships ----
    # The role this user belongs to
    role = relationship("Role", back_populates="users")
    
    # News articles authored by this user
    news_articles = relationship("News", back_populates="author")
    
    # Notices created by this user
    notices = relationship("Notice", back_populates="author")
    
    # Documents uploaded by this user
    documents = relationship("Document", back_populates="uploaded_by_user")
    
    # Forms uploaded by this user
    forms = relationship("Form", back_populates="uploaded_by_user")
    
    # Job applications submitted by this user
    applications = relationship("Application", back_populates="applicant")
    
    # Chat history
    chat_messages = relationship("ChatHistory", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role_id={self.role_id})>"
