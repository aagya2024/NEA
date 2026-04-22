"""
Audit Log Model
================
Stores an audit trail of important actions in the system.

Every significant action (login, create, update, delete) is logged here
for security and compliance. This is immutable — logs are never updated
or deleted.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):
    """
    Database table: 'audit_logs'

    Immutable audit trail for all significant system actions.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Which user performed the action (nullable for system actions)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # What action was performed (e.g., "login", "create", "update", "delete")
    action = Column(String(50), nullable=False, index=True)

    # What resource was affected (e.g., "news", "user", "role")
    resource = Column(String(100), nullable=True)

    # ID of the affected resource
    resource_id = Column(Integer, nullable=True)

    # Additional details as JSON (e.g., changed fields, old/new values)
    details = Column(JSON, nullable=True)

    # IP address of the request
    ip_address = Column(String(50), nullable=True)

    # User agent string
    user_agent = Column(String(500), nullable=True)

    # Timestamp (when this action occurred)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource}')>"
