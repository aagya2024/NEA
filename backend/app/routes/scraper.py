"""
Scraper Routes (Placeholder)
==============================
Endpoints for triggering and managing the NEA website scraper.
Full implementation will come in Phase 6 (AI pipeline).
"""

from fastapi import APIRouter, Depends
from app.middleware.rbac import require_permission

router = APIRouter(prefix="/api/scraper", tags=["Web Scraper"])


@router.post("/trigger")
def trigger_scrape(_=Depends(require_permission("manage_system"))):
    """Trigger a scrape of the NEA website for content ingestion."""
    return {
        "status": "placeholder",
        "message": "Scraper will be implemented in Phase 6. "
                   "It will scrape nea.org.np for news, notices, and documents "
                   "and ingest them into the vector store.",
    }


@router.get("/status")
def get_scraper_status(_=Depends(require_permission("manage_system"))):
    """Get the current status of the scraper."""
    return {
        "status": "idle",
        "last_run": None,
        "documents_scraped": 0,
        "next_scheduled_run": None,
    }
