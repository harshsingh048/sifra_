"""
Task Routes
===========
Handles CRUD operations for freelance tasks/posts.

Endpoints:
    POST   /api/tasks             - Create a new task (clients only)
    GET    /api/tasks             - List all tasks (with filtering)
    GET    /api/tasks/{task_id}   - Get a single task
    PUT    /api/tasks/{task_id}   - Update a task (owner only)
    DELETE /api/tasks/{task_id}   - Delete a task (owner only)
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=201,
    summary="Create a new task",
    description="""
Create a new freelance task/post. Only clients can create tasks.

**Example Request:**
```json
{
    "title": "Need a Website for My Bakery",
    "description": "Looking for a web developer to build a responsive website for my local bakery. Should include menu, contact form, and online ordering integration.",
    "budget": 1500.00,
    "location": "New York, NY"
}
```

**Example Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Need a Website for My Bakery",
    "description": "Looking for a web developer...",
    "budget": 1500.0,
    "location": "New York, NY",
    "status": "open",
    "owner_id": "abc123",
    "owner_name": "Jane's Bakery",
    "application_count": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```
    """,
)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("client")),
):
    """
    Create a new task/post.

    **Requires:** client role

    - **title**: Task title (5-255 chars)
    - **description**: Detailed description (20-5000 chars)
    - **budget**: Budget in USD (positive number)
    - **location**: Task location or 'Remote'
    """
    service = TaskService(db)
    return service.create_task(task_data, current_user.id)


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="List all tasks",
    description="Browse all tasks with filtering, searching, and pagination.",
)
async def list_tasks(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_budget: Optional[float] = Query(None, ge=0, description="Minimum budget"),
    max_budget: Optional[float] = Query(None, ge=0, description="Maximum budget"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    db: Session = Depends(get_db),
):
    """
    List all tasks with advanced filtering.

    - **skip**: Pagination offset
    - **limit**: Max results (default: 20)
    - **status**: Filter by status (open, in_progress, completed, cancelled)
    - **location**: Filter by location
    - **min_budget**: Minimum budget filter
    - **max_budget**: Maximum budget filter
    - **search**: Full-text search in title and description
    """
    service = TaskService(db)
    return service.get_all_tasks(
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        location=location,
        min_budget=min_budget,
        max_budget=max_budget,
        search=search,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    description="View a single task's details including application count.",
)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get a single task by ID.

    - **task_id**: UUID of the task
    """
    service = TaskService(db)
    return service.get_task_by_id(task_id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update a task. Only the task owner can update.",
)
async def update_task(
    task_id: str,
    update_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a task. Only the owner can update.

    - **task_id**: UUID of the task
    - **title**: Updated title
    - **description**: Updated description
    - **budget**: Updated budget
    - **location**: Updated location
    - **status**: Updated status (open, in_progress, completed, cancelled)
    """
    service = TaskService(db)
    return service.update_task(task_id, current_user.id, update_data)


@router.delete(
    "/{task_id}",
    summary="Delete a task",
    description="Delete a task. Only the task owner can delete.",
)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a task. Only the owner can delete.

    - **task_id**: UUID of the task
    """
    service = TaskService(db)
    return service.delete_task(task_id, current_user.id)
