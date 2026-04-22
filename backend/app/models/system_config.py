"""
System Config Model
====================
Key-value store for system-wide configuration settings.

Examples: site title, maintenance mode, scraper schedule, AI model name, etc.
This allows Super Admins to change settings without redeploying.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class SystemConfig(Base):
    """
    Database table: 'system_config'

    Stores system settings as key-value pairs.
    """
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Unique setting key (e.g., "site_title", "maintenance_mode")
    key = Column(String(200), unique=True, nullable=False, index=True)

    # Setting value (stored as string, parsed by the application)
    value = Column(Text, nullable=True)

    # Description of what this setting controls
    description = Column(Text, nullable=True)

    # Who last updated this setting
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value[:20] if self.value else ''}')>"
