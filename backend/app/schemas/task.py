"""
Task Schemas
============
Pydantic models for task-related request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Request Schemas ─────────────────────────────────────────────


class TaskCreate(BaseModel):
    """
    Schema for creating a new task/post.
    Only clients can create tasks.

    Example:
    ```json
    {
        "title": "Need a Website for My Bakery",
        "description": "Looking for a web developer to build a responsive website for my local bakery. Should include menu, contact form, and online ordering.",
        "budget": 1500.00,
        "location": "New York, NY"
    }
    ```
    """

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Task title",
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Detailed task description",
    )
    budget: float = Field(
        ...,
        gt=0,
        description="Budget amount in USD (must be positive)",
    )
    location: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Task location (city, or 'Remote')",
    )


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    All fields are optional.

    Example:
    ```json
    {
        "title": "Updated Website Project",
        "budget": 2000.00,
        "status": "in_progress"
    }
    ```
    """

    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=20, max_length=5000)
    budget: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    status: Optional[str] = Field(None, description="open, in_progress, completed, cancelled")


# ─── Response Schemas ────────────────────────────────────────────


class TaskResponse(BaseModel):
    """
    Task response with owner information.

    Example:
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Need a Website for My Bakery",
        "description": "Looking for a web developer...",
        "budget": 1500.0,
        "location": "New York, NY",
        "status": "open",
        "owner_id": "abc123",
        "owner_name": "John Doe",
        "application_count": 5,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
    ```
    """

    id: str
    title: str
    description: str
    budget: float
    location: str
    status: str
    owner_id: str
    owner_name: Optional[str] = None
    application_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
