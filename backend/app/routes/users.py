"""
User Routes
===========
Handles user profile management and public user browsing.

Endpoints:
    GET    /api/users/me          - Get current user profile
    PUT    /api/users/me          - Update current user profile
    GET    /api/users             - List all users (with filtering)
    GET    /api/users/{user_id}   - Get a specific user's public profile
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the current authenticated user's profile.

    **Authentication required.**
    """
    service = UserService(db=next(get_db()))
    return service.get_current_user(current_user.id)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
    description="""
Update the current user's profile. Only provided fields will be updated.

**Example Request:**
```json
{
    "name": "Jane Updated",
    "bio": "Experienced web developer with 5+ years",
    "skills": "Python, JavaScript, React, FastAPI"
}
```

**Example Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Jane Updated",
    "email": "jane@example.com",
    "role": "freelancer",
    "bio": "Experienced web developer with 5+ years",
    "skills": "Python, JavaScript, React, FastAPI",
    "company_name": null,
    "avatar_url": null,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
}
```
    """,
)
async def update_me(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update the current user's profile.

    - **name**: Updated full name
    - **bio**: Updated biography
    - **skills**: Updated skills (comma-separated)
    - **company_name**: Updated company name
    - **avatar_url**: Updated avatar URL
    """
    service = UserService(db)
    return service.update_profile(current_user.id, update_data)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users",
    description="Browse users with optional role filtering and pagination.",
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    role: Optional[str] = Query(None, description="Filter by role: 'client' or 'freelancer'"),
    db: Session = Depends(get_db),
):
    """
    List users with pagination and optional role filtering.

    - **skip**: Pagination offset (default: 0)
    - **limit**: Max results (default: 20, max: 100)
    - **role**: Optional filter ('client' or 'freelancer')
    """
    service = UserService(db)
    return service.list_users(skip=skip, limit=limit, role=role)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="View a user's public profile by their ID.",
)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a user's public profile.

    - **user_id**: UUID of the user to retrieve
    """
    service = UserService(db)
    return service.get_user_by_id(user_id)
