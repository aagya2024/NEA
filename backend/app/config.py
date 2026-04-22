"""
NEA Intranet Portal - Application Configuration
================================================
This file loads settings from the .env file and makes them
available throughout the application.

HOW IT WORKS:
- We use pydantic-settings to load environment variables
- It looks for a .env file in the backend/ directory
- Each variable below maps to an env variable (case-insensitive)
- You can override any setting with an environment variable
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    To add a new setting:
    1. Add the variable below with a type and default
    2. Add the same variable name to your .env file
    """
    
    # ---------- Database ----------
    # Connection string for PostgreSQL
    # Format: postgresql://username:password@host:port/database_name
    DATABASE_URL: str = "postgresql://nea_user:nea_password@localhost:5432/nea_intranet"
    
    # ---------- JWT Authentication ----------
    # Secret key used to sign JWT tokens (CHANGE THIS IN PRODUCTION!)
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    # Algorithm used for JWT signing
    JWT_ALGORITHM: str = "HS256"
    # How long access tokens last (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # How long refresh tokens last (in days)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ---------- Redis ----------
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ---------- AI / Embeddings ----------
    # Name of the HuggingFace model for text embeddings
    # all-MiniLM-L6-v2 is lightweight (~80MB) and works well
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    # Directory where ChromaDB stores its vector data
    CHROMA_PERSIST_DIR: str = "./vector_store"
    
    # ---------- File Storage ----------
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # ---------- App Settings ----------
    APP_NAME: str = "NEA Intranet Portal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    # Comma-separated list of allowed frontend origins
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # ---------- Super Admin Defaults ----------
    SUPER_ADMIN_EMAIL: str = "admin@nea.org.np"
    SUPER_ADMIN_PASSWORD: str = "admin123"
    SUPER_ADMIN_NAME: str = "Super Administrator"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins string to a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        # Tell pydantic-settings to load from .env file
        env_file = ".env"
        # Allow extra fields from .env that aren't defined here
        extra = "ignore"


# Create a single instance that's imported everywhere
# Usage: from app.config import settings
settings = Settings()
