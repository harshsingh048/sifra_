"""
Dashboard Routes
================
Personalized dashboard endpoints for users.

Endpoints:
    GET /api/dashboard/my-tasks        - Tasks posted by the current user
    GET /api/dashboard/my-applications - Applications submitted by the current user
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.application import ApplicationResponse
from app.schemas.task import TaskResponse
from app.services.application_service import ApplicationService
from app.services.task_service import TaskService

router = APIRouter()


@router.get(
    "/my-tasks",
    response_model=list[TaskResponse],
    summary="My posted tasks",
    description="Get all tasks posted by the current user (clients).",
)
async def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all tasks posted by the current user.

    **Authentication required.**
    Returns tasks ordered by creation date (newest first).
    """
    service = TaskService(db)
    return service.get_tasks_by_owner(current_user.id)


@router.get(
    "/my-applications",
    response_model=list[ApplicationResponse],
    summary="My applied tasks",
    description="Get all applications submitted by the current user (freelancers).",
)
async def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all applications submitted by the current user.

    **Authentication required.**
    Returns applications ordered by creation date (newest first).
    """
    service = ApplicationService(db)
    return service.get_applications_by_applicant(current_user.id)
