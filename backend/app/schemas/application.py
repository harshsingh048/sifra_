"""
Application Schemas
===================
Pydantic models for application-related request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─── Request Schemas ─────────────────────────────────────────────


class ApplicationCreate(BaseModel):
    """
    Schema for applying to a task.
    Only freelancers can apply to tasks.

    Example:
    ```json
    {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "cover_letter": "Hi! I'm a full-stack developer with 5 years of experience. I've built several bakery websites and would love to help with yours. Here are some of my relevant projects..."
    }
    ```
    """

    task_id: str = Field(..., description="UUID of the task to apply to")
    cover_letter: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        description="Cover letter explaining why you're a good fit",
    )


# ─── Response Schemas ────────────────────────────────────────────


class ApplicationResponse(BaseModel):
    """
    Application response with applicant and task info.

    Example:
    ```json
    {
        "id": "app-uuid",
        "task_id": "task-uuid",
        "task_title": "Need a Website for My Bakery",
        "applicant_id": "user-uuid",
        "applicant_name": "Jane Smith",
        "applicant_skills": "Python, JavaScript, React",
        "cover_letter": "Hi! I'm a full-stack developer...",
        "status": "pending",
        "created_at": "2024-01-15T12:00:00Z",
        "updated_at": "2024-01-15T12:00:00Z"
    }
    ```
    """

    id: str
    task_id: str
    task_title: Optional[str] = None
    applicant_id: str
    applicant_name: Optional[str] = None
    applicant_skills: Optional[str] = None
    cover_letter: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
