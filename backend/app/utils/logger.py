"""
Logger Utility
==============
Structured logging for the NEA Intranet Portal.

USAGE:
    from app.utils.logger import logger
    
    logger.info("User logged in", extra={"user_id": 1})
    logger.error("Database connection failed", exc_info=True)
"""

import logging
import sys
from app.config import settings


def setup_logger(name: str = "nea_intranet") -> logging.Logger:
    """
    Create and configure a structured logger.
    
    Features:
    - Outputs to stdout (captured by Docker/systemd)
    - Includes timestamp, level, module, and message
    - Debug level in development, Info level in production
    """
    _logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers if called multiple times
    if _logger.handlers:
        return _logger
    
    # Set log level based on DEBUG setting
    _logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Console handler — writes to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Format: timestamp | level | module | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s.%(module)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    
    return _logger


# Create a single logger instance used across the application
logger = setup_logger()
