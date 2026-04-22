"""
NEA Intranet Portal - Database Models Package
===============================================
This file imports all models so that SQLAlchemy knows about them.

WHY THIS IS NEEDED:
When we run Alembic migrations or create tables, SQLAlchemy needs
to know about ALL our models. By importing them here, we ensure
they're all registered with the Base class.

USAGE:
    from app.models import User, Role, Permission, News, etc.
"""

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission, RolePermission
from app.models.news import News
from app.models.notice import Notice
from app.models.document import Document
from app.models.form import Form
from app.models.act import Act
from app.models.recruitment import Recruitment
from app.models.application import Application
from app.models.chat_history import ChatHistory
from app.models.system_config import SystemConfig
from app.models.log import AuditLog

# This list makes it easy to see all models at a glance
__all__ = [
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "News",
    "Notice",
    "Document",
    "Form",
    "Act",
    "Recruitment",
    "Application",
    "ChatHistory",
    "SystemConfig",
    "AuditLog",
]
