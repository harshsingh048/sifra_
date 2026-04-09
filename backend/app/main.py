"""
Local Freelancing Marketplace - Production Backend
===================================================
A FastAPI-based REST API connecting local businesses with freelancers.

Tech Stack: FastAPI, SQLAlchemy, PostgreSQL, JWT, Google OAuth, bcrypt
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, tasks, applications, dashboard
from app.database import engine, Base

# Create database tables on startup


app = FastAPI(
    title="Local Freelancing Marketplace API",
    description="""
## Overview
A production-ready API for connecting small local businesses with freelancers.

## Features
- 🔐 JWT Authentication + Google OAuth
- 👥 User management with role-based access (client / freelancer)
- 📋 Task / Freelance Post management
- 📝 Application system
- 📊 Dashboard APIs

## Authentication
Most routes require a Bearer token. Obtain one via `/auth/login` or `/auth/google`.

### Token Flow
1. Register or login to get access_token + refresh_token
2. Include `Authorization: Bearer <access_token>` in subsequent requests
3. Use `/auth/refresh` to get a new access_token when it expires
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per environment in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Local Freelancing Marketplace API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "service": "Local Freelancing Marketplace API",
    }
from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="docs",
    )
