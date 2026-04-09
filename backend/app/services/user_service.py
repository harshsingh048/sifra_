"""
User Service
============
Handles user profile management and retrieval.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate


class UserService:
    """
    Service class for user-related operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_current_user(self, user_id: str) -> UserResponse:
        """
        Get the current authenticated user's profile.

        Args:
            user_id: UUID of the authenticated user.

        Returns:
            UserResponse with user details.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)

    def update_profile(self, user_id: str, update_data: UserUpdate) -> UserResponse:
        """
        Update the current user's profile.
        Only provided fields are updated (partial update).

        Args:
            user_id: UUID of the authenticated user.
            update_data: Fields to update.

        Returns:
            Updated UserResponse.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return UserResponse.model_validate(user)

    def get_user_by_id(self, user_id: str) -> UserResponse:
        """
        Get a public user profile by ID.
        Returns basic info (no sensitive data).

        Args:
            user_id: UUID of the user to retrieve.

        Returns:
            UserResponse with public profile data.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)

    def list_users(
        self, skip: int = 0, limit: int = 20, role: Optional[str] = None
    ) -> List[UserResponse]:
        """
        List users with optional role filtering.
        Used for browsing freelancers or clients.

        Args:
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.
            role: Optional role filter ('client' or 'freelancer').

        Returns:
            List of UserResponse objects.
        """
        query = self.db.query(User).filter(User.is_active == True)

        if role:
            query = query.filter(User.role == role)

        users = query.offset(skip).limit(limit).all()
        return [UserResponse.model_validate(u) for u in users]
