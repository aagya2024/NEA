"""
NEA Intranet Portal - Database Setup
=====================================
This file sets up the connection to PostgreSQL using SQLAlchemy.

KEY CONCEPTS FOR BEGINNERS:
- Engine: The connection to the database (like a phone line)
- Session: A conversation with the database (like a phone call)
- Base: The parent class for all our database models (tables)
- get_db: A function that gives each API request its own session

HOW IT WORKS:
1. We create an Engine that knows how to connect to PostgreSQL
2. We create a SessionLocal factory that makes new sessions
3. Each API request gets a session via get_db()
4. The session is automatically closed when the request is done
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# ---- Step 1: Create the database engine ----
# The engine manages the actual connection to the database
# echo=False means don't print every SQL query (set True for debugging)
_engine_kwargs = {"echo": False}

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread=False for FastAPI (multi-threaded)
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL supports connection pooling
    _engine_kwargs.update(
        pool_size=10,        # Keep 10 connections ready
        max_overflow=20,     # Allow up to 20 extra connections if needed
        pool_pre_ping=True,  # Test connections before using them
    )

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

# ---- Step 2: Create a session factory ----
# This is like a template for creating database sessions
# autocommit=False means we manually control when changes are saved
# autoflush=False means we manually control when changes are sent to DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---- Step 3: Create the Base class ----
# All our models (User, Role, News, etc.) will inherit from this
# This tells SQLAlchemy they should be treated as database tables
Base = declarative_base()


# ---- Step 4: Dependency function for FastAPI ----
def get_db() -> Generator[Session, None, None]:
    """
    Get a database session for an API request.
    
    This is used as a FastAPI dependency:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    
    The 'yield' keyword means:
    1. Create a session and give it to the request handler
    2. When the request is done, close the session
    3. If there was an error, the session is still closed (finally block)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
