"""
News Routes
============
CRUD endpoints for news articles.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.news import NewsCreate, NewsUpdate, NewsResponse, NewsListResponse
from app.services import news_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission
from fastapi import HTTPException

router = APIRouter(prefix="/api/news", tags=["News"])


@router.get("", response_model=NewsListResponse)
def list_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List news articles (paginated)."""
    return news_service.get_news_list(db, page, per_page, category, published_only=False, search=search)


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single news article by ID."""
    news = news_service.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    
    result = NewsResponse.model_validate(news)
    if news.author:
        result.author_name = news.author.full_name
    return result


@router.post("", response_model=NewsResponse, status_code=201)
def create_news(
    news_data: NewsCreate,
    current_user: User = Depends(require_permission("create_news")),
    db: Session = Depends(get_db),
):
    """Create a new news article."""
    return news_service.create_news(db, news_data, current_user)


@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int,
    news_data: NewsUpdate,
    _=Depends(require_permission("edit_news")),
    db: Session = Depends(get_db),
):
    """Update a news article."""
    return news_service.update_news(db, news_id, news_data)


@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    _=Depends(require_permission("delete_news")),
    db: Session = Depends(get_db),
):
    """Delete a news article."""
    news_service.delete_news(db, news_id)
    return {"message": "News article deleted successfully"}
