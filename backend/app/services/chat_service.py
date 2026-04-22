"""
Chat Service
=============
Intelligent chatbot that queries NEA database content to answer user questions.

Searches across news, notices, documents, forms, acts, and recruitment
to provide real, contextual answers from the intranet data.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.chat_history import ChatHistory
from app.models.news import News
from app.models.notice import Notice
from app.models.document import Document
from app.models.form import Form
from app.models.act import Act
from app.models.recruitment import Recruitment
from app.utils.logger import logger


# ---- Keyword Helpers ----

def _extract_keywords(message: str) -> list[str]:
    """Extract meaningful keywords from user message."""
    stop_words = {
        'i', 'me', 'my', 'the', 'a', 'an', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
        'am', 'it', 'its', 'of', 'in', 'to', 'for', 'with', 'on', 'at',
        'by', 'from', 'as', 'into', 'about', 'between', 'through',
        'and', 'but', 'or', 'not', 'no', 'so', 'if', 'than', 'too',
        'very', 'just', 'how', 'all', 'each', 'every', 'any', 'some',
        'such', 'only', 'own', 'same', 'also', 'tell', 'show', 'give',
        'get', 'find', 'help', 'please', 'thanks', 'thank', 'you',
        'there', 'here', 'where', 'when', 'why', 'up', 'out',
        'know', 'want', 'need', 'like', 'looking', 'look', 'see',
        'hi', 'hello', 'hey', 'good', 'morning', 'afternoon', 'evening',
    }
    words = message.lower().split()
    keywords = [w.strip('?.,!;:') for w in words if len(w) > 2 and w.strip('?.,!;:') not in stop_words]
    return keywords


def _detect_intent(message: str) -> str:
    """Detect what kind of content the user is asking about."""
    msg = message.lower()
    
    if any(w in msg for w in ['news', 'article', 'latest news', 'headlines', 'updates']):
        return 'news'
    if any(w in msg for w in ['notice', 'circular', 'announcement', 'alert']):
        return 'notices'
    if any(w in msg for w in ['document', 'file', 'report', 'paper', 'download']):
        return 'documents'
    if any(w in msg for w in ['form', 'template', 'application form']):
        return 'forms'
    if any(w in msg for w in ['act', 'bylaw', 'law', 'regulation', 'policy', 'rule', 'legislation']):
        return 'acts'
    if any(w in msg for w in ['job', 'recruit', 'vacancy', 'hiring', 'career', 'position', 'opening', 'apply', 'employment']):
        return 'recruitment'
    if any(w in msg for w in ['help', 'can you', 'what can', 'how to', 'guide', 'feature']):
        return 'help'
    if any(w in msg for w in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste']):
        return 'greeting'
    
    return 'general'


# ---- Database Search Functions ----

def _search_news(db: Session, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search news articles by keywords."""
    query = db.query(News)
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(News.title.ilike(f"%{kw}%"))
            filters.append(News.content.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    results = query.order_by(News.created_at.desc()).limit(limit).all()
    return [{"id": n.id, "title": n.title, "type": "news", "date": str(n.created_at)} for n in results]


def _search_notices(db: Session, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search notices by keywords."""
    query = db.query(Notice)
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Notice.title.ilike(f"%{kw}%"))
            filters.append(Notice.content.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    results = query.order_by(Notice.created_at.desc()).limit(limit).all()
    return [{"id": n.id, "title": n.title, "type": "notice", "priority": getattr(n, 'priority', None), "date": str(n.created_at)} for n in results]


def _search_documents(db: Session, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search documents by keywords."""
    query = db.query(Document)
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Document.title.ilike(f"%{kw}%"))
            if hasattr(Document, 'description'):
                filters.append(Document.description.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    results = query.order_by(Document.created_at.desc()).limit(limit).all()
    return [{"id": d.id, "title": d.title, "type": "document", "date": str(d.created_at)} for d in results]


def _search_forms(db: Session, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search forms by keywords."""
    query = db.query(Form)
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Form.title.ilike(f"%{kw}%"))
            if hasattr(Form, 'description'):
                filters.append(Form.description.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    results = query.order_by(Form.created_at.desc()).limit(limit).all()
    return [{"id": f.id, "title": f.title, "type": "form", "date": str(f.created_at)} for f in results]


def _search_acts(db: Session, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search acts and bylaws by keywords."""
    query = db.query(Act)
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Act.title.ilike(f"%{kw}%"))
            if hasattr(Act, 'description'):
                filters.append(Act.description.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    results = query.order_by(Act.created_at.desc()).limit(limit).all()
    return [{"id": a.id, "title": a.title, "type": "act", "date": str(a.created_at)} for a in results]


def _search_recruitment(db: Session, keywords: list[str], limit: int = 5) -> list[dict]:
    """Search recruitment/job postings by keywords."""
    query = db.query(Recruitment)
    if keywords:
        filters = []
        for kw in keywords:
            filters.append(Recruitment.title.ilike(f"%{kw}%"))
            if hasattr(Recruitment, 'description'):
                filters.append(Recruitment.description.ilike(f"%{kw}%"))
        query = query.filter(or_(*filters))
    results = query.order_by(Recruitment.created_at.desc()).limit(limit).all()
    return [{"id": r.id, "title": r.title, "type": "recruitment", "date": str(r.created_at)} for r in results]


def _search_all(db: Session, keywords: list[str]) -> list[dict]:
    """Search across all content types."""
    all_results = []
    all_results.extend(_search_news(db, keywords, 3))
    all_results.extend(_search_notices(db, keywords, 3))
    all_results.extend(_search_documents(db, keywords, 3))
    all_results.extend(_search_forms(db, keywords, 2))
    all_results.extend(_search_acts(db, keywords, 2))
    all_results.extend(_search_recruitment(db, keywords, 2))
    return all_results


# ---- Stats Helpers ----

def _get_portal_stats(db: Session) -> dict:
    """Get current content counts from the portal."""
    return {
        "news": db.query(func.count(News.id)).scalar() or 0,
        "notices": db.query(func.count(Notice.id)).scalar() or 0,
        "documents": db.query(func.count(Document.id)).scalar() or 0,
        "forms": db.query(func.count(Form.id)).scalar() or 0,
        "acts": db.query(func.count(Act.id)).scalar() or 0,
        "recruitment": db.query(func.count(Recruitment.id)).scalar() or 0,
    }


# ---- Response Builders ----

def _format_results(results: list[dict], category: str) -> str:
    """Format search results into a readable response."""
    if not results:
        return f"I couldn't find any {category} matching your query. The portal might not have any {category} content yet. You can add content through the relevant section in the sidebar."
    
    lines = [f"Here's what I found ({len(results)} {category}):\n"]
    for i, item in enumerate(results, 1):
        title = item.get('title', 'Untitled')
        extra = ""
        if item.get('priority'):
            extra = f" [{item['priority'].upper()}]"
        lines.append(f"  {i}. {title}{extra}")
    
    lines.append(f"\nYou can view these in the {category.title()} section from the sidebar.")
    return "\n".join(lines)


def _build_greeting_response() -> str:
    """Build a greeting response."""
    return (
        "Hello! 👋 I'm the NEA AI Assistant. I can help you with:\n\n"
        "📰 **News** — Find the latest news articles\n"
        "📢 **Notices** — Search circulars and announcements\n"
        "📄 **Documents** — Look for reports and files\n"
        "📋 **Forms** — Find application forms and templates\n"
        "⚖️ **Acts & Bylaws** — Search regulations and policies\n"
        "💼 **Recruitment** — Check job openings and vacancies\n\n"
        "Just ask me anything, like:\n"
        '• "Show me the latest notices"\n'
        '• "Are there any job openings?"\n'
        '• "Find documents about electricity"\n'
        '• "What acts are available?"'
    )


def _build_help_response() -> str:
    """Build a help response."""
    return (
        "I can help you navigate the NEA Intranet Portal! Here's what I can do:\n\n"
        "🔍 **Search Content** — Ask me to find news, notices, documents, forms, acts, or job postings\n"
        "📊 **Portal Stats** — Ask \"how many documents are there?\" to see content counts\n"
        "📢 **Latest Updates** — Ask for the latest news or notices\n"
        "💼 **Job Openings** — Ask about current recruitment opportunities\n\n"
        "Try asking something like:\n"
        '• "What are the latest news articles?"\n'
        '• "Find notices about salary"\n'
        '• "Are there any open positions?"\n'
        '• "Show me available forms"'
    )


# ---- Main Chat Function ----

def chat_with_ai(
    db: Session,
    user_id: int,
    message: str,
    session_id: Optional[str] = None,
) -> dict:
    """
    Process a user message and return an intelligent response
    by searching the NEA database content.
    """
    intent = _detect_intent(message)
    keywords = _extract_keywords(message)
    sources = []
    
    if intent == 'greeting':
        response_text = _build_greeting_response()
    
    elif intent == 'help':
        response_text = _build_help_response()
    
    elif intent == 'news':
        results = _search_news(db, keywords)
        sources = results
        response_text = _format_results(results, "news articles")
    
    elif intent == 'notices':
        results = _search_notices(db, keywords)
        sources = results
        response_text = _format_results(results, "notices")
    
    elif intent == 'documents':
        results = _search_documents(db, keywords)
        sources = results
        response_text = _format_results(results, "documents")
    
    elif intent == 'forms':
        results = _search_forms(db, keywords)
        sources = results
        response_text = _format_results(results, "forms")
    
    elif intent == 'acts':
        results = _search_acts(db, keywords)
        sources = results
        response_text = _format_results(results, "acts & bylaws")
    
    elif intent == 'recruitment':
        results = _search_recruitment(db, keywords)
        sources = results
        response_text = _format_results(results, "job postings")
    
    else:
        # General query — search across all content
        if keywords:
            results = _search_all(db, keywords)
            sources = results
            if results:
                # Group results by type
                grouped = {}
                for r in results:
                    t = r['type']
                    grouped.setdefault(t, []).append(r)
                
                lines = [f"I searched across the portal for \"{' '.join(keywords[:3])}\". Here's what I found:\n"]
                for content_type, items in grouped.items():
                    lines.append(f"**{content_type.title()}** ({len(items)} found):")
                    for item in items:
                        lines.append(f"  • {item['title']}")
                    lines.append("")
                
                lines.append("You can navigate to the relevant section in the sidebar for more details.")
                response_text = "\n".join(lines)
            else:
                stats = _get_portal_stats(db)
                total = sum(stats.values())
                if total == 0:
                    response_text = (
                        "The portal doesn't have any content yet. As an administrator, you can start adding:\n\n"
                        "📰 News articles from the News section\n"
                        "📢 Notices from the Notices section\n"
                        "📄 Documents from the Documents section\n"
                        "📋 Forms from the Forms section\n"
                        "⚖️ Acts & Bylaws from the Acts section\n"
                        "💼 Job postings from the Recruitment section\n\n"
                        "Once content is added, I'll be able to search and find information for you!"
                    )
                else:
                    response_text = (
                        f"I couldn't find results matching your query. "
                        f"The portal currently has: "
                        f"{stats['news']} news articles, "
                        f"{stats['notices']} notices, "
                        f"{stats['documents']} documents, "
                        f"{stats['forms']} forms, "
                        f"{stats['acts']} acts, and "
                        f"{stats['recruitment']} job postings.\n\n"
                        "Try being more specific, or ask me for help to see what I can do!"
                    )
        else:
            response_text = _build_help_response()

    # Save to chat history
    chat = ChatHistory(
        user_id=user_id,
        message=message,
        response=response_text,
        sources=sources,
        session_id=session_id,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)

    logger.info(f"Chat message processed for user {user_id} (intent: {intent})")

    return {
        "id": chat.id,
        "message": message,
        "response": response_text,
        "sources": sources,
        "session_id": session_id,
        "created_at": str(chat.created_at),
    }


def get_chat_history(
    db: Session,
    user_id: int,
    session_id: Optional[str] = None,
    limit: int = 50,
) -> list[ChatHistory]:
    """Get chat history for a user, optionally filtered by session."""
    query = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)
    return query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
