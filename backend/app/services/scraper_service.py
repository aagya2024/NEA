"""
Scraper Service
================
Placeholder for the web scraper that fetches content from nea.org.np.

This will be implemented when the AI module is built. For now, it
provides a status endpoint and a placeholder sync trigger.
"""

from app.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory scraper status
_scraper_status = {
    "is_running": False,
    "last_run": None,
    "last_result": None,
    "items_scraped": 0,
}


def get_scraper_status() -> dict:
    """Get the current scraper status."""
    return _scraper_status.copy()


def trigger_scrape() -> dict:
    """
    Trigger a website scrape.
    
    Placeholder — will be replaced with actual BeautifulSoup scraper.
    """
    logger.info("Scraper trigger called (placeholder)")
    
    return {
        "message": "Scraper module is not yet implemented. "
                   "It will fetch news, notices, and acts from nea.org.np.",
        "status": "pending_implementation",
    }
