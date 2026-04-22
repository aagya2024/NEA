"""
News Service
=============
CRUD operations for news articles with publish/unpublish workflow.
"""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.news import News
from app.models.user import User
from app.schemas.news import NewsCreate, NewsUpdate
from app.utils.logger import logger

try:
    from slugify import slugify
except ImportError:
    def slugify(text: str) -> str:
        return text.lower().replace(" ", "-")


def create_news(db: Session, data: NewsCreate, author_id: int) -> News:
    news = News(
        title=data.title,
        content=data.content,
        category=data.category,
        slug=slugify(data.title),
        is_published=data.is_published,
        published_at=datetime.now(timezone.utc) if data.is_published else None,
        author_id=author_id,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    logger.info(f"News created: {news.title}")
    return news


def get_news_by_id(db: Session, news_id: int) -> Optional[News]:
    return db.query(News).filter(News.id == news_id).first()


def get_news_list(
    db: Session,
    page: int = 1,
    per_page: int = 20,
    published_only: bool = False,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[News], int]:
    query = db.query(News)

    if published_only:
        query = query.filter(News.is_published == True)
    if category:
        query = query.filter(News.category == category)
    if search:
        query = query.filter(News.title.ilike(f"%{search}%"))

    total = query.count()
    news = query.order_by(News.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return news, total


def update_news(db: Session, news_id: int, data: NewsUpdate) -> Optional[News]:
    news = get_news_by_id(db, news_id)
    if not news:
        return None

    update_data = data.model_dump(exclude_unset=True)
    
    # Handle publish transition
    if "is_published" in update_data and update_data["is_published"] and not news.is_published:
        news.published_at = datetime.now(timezone.utc)
    
    if "title" in update_data:
        news.slug = slugify(update_data["title"])

    for field, value in update_data.items():
        setattr(news, field, value)

    db.commit()
    db.refresh(news)
    return news


def delete_news(db: Session, news_id: int) -> bool:
    news = get_news_by_id(db, news_id)
    if not news:
        return False
    db.delete(news)
    db.commit()
    logger.info(f"News deleted: {news.title}")
    return True


def increment_view_count(db: Session, news_id: int):
    news = get_news_by_id(db, news_id)
    if news:
        news.view_count = (news.view_count or 0) + 1
        db.commit()
