"""
News Routes
============
Endpoints: GET /news, GET /news/{id}, POST /news, PUT /news/{id}, DELETE /news/{id}
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.news import NewsCreate, NewsUpdate, NewsResponse, NewsListResponse
from app.services import news_service
from app.utils.security import get_current_user
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter(prefix="/api/news", tags=["News"])


@router.get("", response_model=NewsListResponse)
def list_news(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    published_only: bool = True,
    db: Session = Depends(get_db),
):
    """List news articles (published by default)."""
    news_list, total = news_service.get_news_list(db, page, per_page, published_only, category, search)
    items = []
    for n in news_list:
        resp = NewsResponse.model_validate(n)
        resp.author_name = n.author.full_name if n.author else None
        items.append(resp)
    return NewsListResponse(news=items, total=total, page=page, per_page=per_page)


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(news_id: int, db: Session = Depends(get_db)):
    """Get a news article by ID."""
    news = news_service.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    news_service.increment_view_count(db, news_id)
    resp = NewsResponse.model_validate(news)
    resp.author_name = news.author.full_name if news.author else None
    return resp


@router.post("", response_model=NewsResponse, status_code=201)
def create_news(
    data: NewsCreate,
    current_user: User = Depends(require_permission("create_news")),
    db: Session = Depends(get_db),
):
    """Create a new news article."""
    news = news_service.create_news(db, data, current_user.id)
    return NewsResponse.model_validate(news)


@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int, data: NewsUpdate,
    current_user: User = Depends(require_permission("edit_news")),
    db: Session = Depends(get_db),
):
    """Update a news article."""
    news = news_service.update_news(db, news_id, data)
    if not news:
        raise HTTPException(status_code=404, detail="News article not found")
    return NewsResponse.model_validate(news)


@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    current_user: User = Depends(require_permission("delete_news")),
    db: Session = Depends(get_db),
):
    """Delete a news article."""
    if not news_service.delete_news(db, news_id):
        raise HTTPException(status_code=404, detail="News article not found")
    return {"message": "News article deleted"}
