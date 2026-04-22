"""
NEA Intranet Portal - FastAPI Application
==========================================
Main entry point that wires everything together:
- Router registration for all API endpoints
- CORS middleware for frontend communication
- Startup events for database initialization and seed data
- Health check endpoint

RUN WITH:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.utils.logger import logger

# Import all models so SQLAlchemy registers them for table creation
from app.models import (  # noqa: F401
    User, Role, Permission, RolePermission, News, Notice,
    Document, Form, Act, Recruitment, Application,
    ChatHistory, SystemConfig, AuditLog,
)

# Import all route modules
from app.routes import auth, users, roles, news, notices, documents, forms, acts, recruitment, chat, scraper, system


# ---- Seed Data ----

def seed_database():
    """
    Create default roles, permissions, and a super admin user
    on first startup (if they don't already exist).
    """
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app.utils.security import hash_password

    db: Session = SessionLocal()
    try:
        # ---- 1. Create default roles ----
        default_roles = [
            {"name": "Super Admin", "description": "Full system access", "is_system_role": True},
            {"name": "Admin", "description": "Content management and user administration", "is_system_role": True},
            {"name": "HR", "description": "Human resources management", "is_system_role": True},
            {"name": "Employee", "description": "Standard employee access", "is_system_role": True},
            {"name": "Viewer", "description": "Read-only access", "is_system_role": True},
        ]

        for role_data in default_roles:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                db.add(Role(**role_data))
                logger.info(f"Created role: {role_data['name']}")

        db.commit()

        # ---- 2. Create default permissions ----
        default_permissions = [
            # News
            {"key": "create_news", "name": "Create News Articles", "module": "news"},
            {"key": "edit_news", "name": "Edit News Articles", "module": "news"},
            {"key": "delete_news", "name": "Delete News Articles", "module": "news"},
            # Notices
            {"key": "create_notice", "name": "Create Notices", "module": "notices"},
            {"key": "edit_notice", "name": "Edit Notices", "module": "notices"},
            {"key": "delete_notice", "name": "Delete Notices", "module": "notices"},
            # Documents
            {"key": "upload_document", "name": "Upload Documents", "module": "documents"},
            {"key": "edit_document", "name": "Edit Documents", "module": "documents"},
            {"key": "delete_document", "name": "Delete Documents", "module": "documents"},
            # Forms
            {"key": "upload_form", "name": "Upload Forms", "module": "forms"},
            {"key": "edit_form", "name": "Edit Forms", "module": "forms"},
            {"key": "delete_form", "name": "Delete Forms", "module": "forms"},
            # Acts
            {"key": "manage_acts", "name": "Manage Acts & Bylaws", "module": "acts"},
            # Recruitment
            {"key": "manage_recruitment", "name": "Manage Recruitment", "module": "recruitment"},
            # Users & Roles
            {"key": "manage_users", "name": "Manage Users", "module": "users"},
            {"key": "manage_roles", "name": "Manage Roles & Permissions", "module": "roles"},
            # System
            {"key": "manage_system", "name": "Manage System Settings", "module": "system"},
            {"key": "view_logs", "name": "View Audit Logs", "module": "system"},
        ]

        for perm_data in default_permissions:
            existing = db.query(Permission).filter(Permission.key == perm_data["key"]).first()
            if not existing:
                db.add(Permission(**perm_data))
                logger.info(f"Created permission: {perm_data['key']}")

        db.commit()

        # ---- 3. Assign ALL permissions to Super Admin ----
        super_admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
        if super_admin_role:
            all_perms = db.query(Permission).all()
            for perm in all_perms:
                existing = (
                    db.query(RolePermission)
                    .filter(
                        RolePermission.role_id == super_admin_role.id,
                        RolePermission.permission_id == perm.id,
                    )
                    .first()
                )
                if not existing:
                    db.add(RolePermission(role_id=super_admin_role.id, permission_id=perm.id))
            db.commit()

        # ---- 4. Assign permissions to Admin role ----
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if admin_role:
            admin_perm_keys = [
                "create_news", "edit_news", "delete_news",
                "create_notice", "edit_notice", "delete_notice",
                "upload_document", "edit_document", "delete_document",
                "upload_form", "edit_form", "delete_form",
                "manage_acts", "manage_users",
            ]
            for key in admin_perm_keys:
                perm = db.query(Permission).filter(Permission.key == key).first()
                if perm:
                    existing = (
                        db.query(RolePermission)
                        .filter(RolePermission.role_id == admin_role.id, RolePermission.permission_id == perm.id)
                        .first()
                    )
                    if not existing:
                        db.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))
            db.commit()

        # ---- 5. Assign permissions to HR role ----
        hr_role = db.query(Role).filter(Role.name == "HR").first()
        if hr_role:
            hr_perm_keys = ["manage_recruitment", "create_notice", "edit_notice"]
            for key in hr_perm_keys:
                perm = db.query(Permission).filter(Permission.key == key).first()
                if perm:
                    existing = (
                        db.query(RolePermission)
                        .filter(RolePermission.role_id == hr_role.id, RolePermission.permission_id == perm.id)
                        .first()
                    )
                    if not existing:
                        db.add(RolePermission(role_id=hr_role.id, permission_id=perm.id))
            db.commit()

        # ---- 6. Create Super Admin user ----
        super_admin_user = db.query(User).filter(User.email == settings.SUPER_ADMIN_EMAIL).first()
        if not super_admin_user and super_admin_role:
            super_admin_user = User(
                email=settings.SUPER_ADMIN_EMAIL,
                full_name=settings.SUPER_ADMIN_NAME,
                password_hash=hash_password(settings.SUPER_ADMIN_PASSWORD),
                role_id=super_admin_role.id,
                is_active=True,
            )
            db.add(super_admin_user)
            db.commit()
            logger.info(f"Created super admin: {settings.SUPER_ADMIN_EMAIL}")

        # ---- 7. Create default users for each role ----
        default_users = [
            {"email": "admin.user@nea.org.np", "full_name": "Admin User", "password": "admin123", "role_name": "Admin"},
            {"email": "hr.user@nea.org.np", "full_name": "HR User", "password": "hr123", "role_name": "HR"},
            {"email": "employee@nea.org.np", "full_name": "Employee User", "password": "employee123", "role_name": "Employee"},
            {"email": "viewer@nea.org.np", "full_name": "Viewer User", "password": "viewer123", "role_name": "Viewer"},
        ]

        for user_data in default_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                role = db.query(Role).filter(Role.name == user_data["role_name"]).first()
                if role:
                    new_user = User(
                        email=user_data["email"],
                        full_name=user_data["full_name"],
                        password_hash=hash_password(user_data["password"]),
                        role_id=role.id,
                        is_active=True,
                    )
                    db.add(new_user)
                    logger.info(f"Created {user_data['role_name']} user: {user_data['email']}")
        db.commit()

        logger.info("Database seeding complete!")

    except Exception as e:
        db.rollback()
        logger.error(f"Seeding error: {e}")
    finally:
        db.close()


# ---- Application Lifecycle ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the FastAPI application.
    
    On startup:
    1. Create all database tables (if they don't exist)
    2. Seed with default roles, permissions, and super admin user
    """
    logger.info("Starting NEA Intranet Portal...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Seed default data
    seed_database()

    logger.info(f"NEA Intranet Portal v{settings.APP_VERSION} is ready!")
    
    yield
    
    logger.info("Shutting down NEA Intranet Portal...")


# ---- Create FastAPI Application ----

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Internal intranet portal for Nepal Electricity Authority. "
                "Features content management, document repository, recruitment, "
                "and an AI-powered knowledge assistant.",
    lifespan=lifespan,
)

# ---- CORS Middleware ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Register Routers ----
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(news.router)
app.include_router(notices.router)
app.include_router(documents.router)
app.include_router(forms.router)
app.include_router(acts.router)
app.include_router(recruitment.router)
app.include_router(chat.router)
app.include_router(scraper.router)
app.include_router(system.router)


# ---- Health Check ----
@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint — confirms the API is running."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    """Health check for load balancers and monitoring."""
    return {"status": "healthy"}
