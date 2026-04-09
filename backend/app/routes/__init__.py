"""
Routes Package
==============
FastAPI routers grouped by domain.
"""

from app.routes import auth, users, tasks, applications, dashboard

__all__ = ["auth", "users", "tasks", "applications", "dashboard"]
