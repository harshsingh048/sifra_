"""
Application Routes
==================
Handles freelancer applications to tasks.

Endpoints:
    POST   /api/applications                    - Apply to a task
    GET    /api/applications/task/{task_id}     - View applicants for a task (owner only)
    PUT    /api/applications/{app_id}/status    - Update application status (owner only)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.services.application_service import ApplicationService

router = APIRouter()


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201,
    summary="Apply to a task",
    description="""
Submit an application to a freelance task. Only freelancers can apply.

**Example Request:**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "cover_letter": "Hi! I'm a full-stack developer with 5 years of experience. I've built several bakery websites and would love to help with yours. My portfolio includes..."
}
```

**Example Response:**
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
    """,
)
async def apply_to_task(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("freelancer")),
):
    """
    Apply to a task as a freelancer.

    **Requires:** freelancer role

    - **task_id**: UUID of the task to apply to
    - **cover_letter**: Your application message (20-5000 chars)
    """
    service = ApplicationService(db)
    return service.apply_to_task(application_data, current_user.id)


@router.get(
    "/task/{task_id}",
    response_model=list[ApplicationResponse],
    summary="View applicants for a task",
    description="View all applications for a specific task. Only the task owner can view.",
)
async def get_applicants(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all applications for a task.

    **Requires:** Task ownership

    - **task_id**: UUID of the task
    """
    service = ApplicationService(db)
    return service.get_applicants_for_task(task_id, current_user.id)


@router.put(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    summary="Update application status",
    description="Accept or reject an application. Only the task owner can update status.",
)
async def update_application_status(
    application_id: str,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update the status of an application.

    **Requires:** Task ownership

    - **application_id**: UUID of the application
    - **status**: New status ('accepted' or 'rejected')

    **Example Request:**
    ```json
    {
        "status": "accepted"
    }
    ```
    """
    new_status = status_update.get("status")
    if not new_status:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="status is required")

    service = ApplicationService(db)
    return service.update_application_status(application_id, new_status, current_user.id)
