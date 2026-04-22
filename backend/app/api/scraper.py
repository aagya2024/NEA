"""
Scraper Routes
===============
Endpoints for controlling the web scraper (nea.org.np).
"""

from fastapi import APIRouter, Depends
from app.middleware.rbac import require_permission
from app.services import scraper_service

router = APIRouter(prefix="/api/scraper", tags=["Scraper"])


@router.post("/sync")
def trigger_sync(
    _=Depends(require_permission("system_config")),
):
    """Trigger a web scrape of nea.org.np content."""
    return scraper_service.trigger_scrape()


@router.get("/status")
def get_status(
    _=Depends(require_permission("system_config")),
):
    """Get the current scraper status."""
    return scraper_service.get_scraper_status()
