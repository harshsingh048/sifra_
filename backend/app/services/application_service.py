"""
Application Service
===================
Handles freelancer applications to tasks.
"""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.task import Task
from app.schemas.application import ApplicationCreate, ApplicationResponse


class ApplicationService:
    """
    Service class for application-related operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def apply_to_task(
        self, application_data: ApplicationCreate, applicant_id: str
    ) -> ApplicationResponse:
        """
        Submit an application to a task.

        Steps:
        1. Verify the task exists and is open.
        2. Check for duplicate applications.
        3. Create the application.

        Args:
            application_data: Validated application data.
            applicant_id: UUID of the freelancer applying.

        Returns:
            ApplicationResponse with application details.

        Raises:
            HTTPException: If task not found, not open, or duplicate application.
        """
        # Verify task exists
        task = self.db.query(Task).filter(Task.id == application_data.task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Verify task is open
        if task.status != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot apply to a task with status '{task.status}'. Task must be 'open'.",
            )

        # Prevent self-application
        if task.owner_id == applicant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot apply to your own task",
            )

        # Check for duplicate application
        existing = (
            self.db.query(Application)
            .filter(
                Application.task_id == application_data.task_id,
                Application.applicant_id == applicant_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already applied to this task",
            )

        # Create application
        application = Application(
            task_id=application_data.task_id,
            applicant_id=applicant_id,
            cover_letter=application_data.cover_letter,
            status="pending",
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)

        return self._to_response(application)

    def get_applicants_for_task(
        self, task_id: str, owner_id: str
    ) -> List[ApplicationResponse]:
        """
        Get all applications for a specific task.
        Only the task owner can view applicants.

        Args:
            task_id: UUID of the task.
            owner_id: UUID of the requesting user.

        Returns:
            List of ApplicationResponse objects.

        Raises:
            HTTPException: If task not found or user is not the owner.
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        if task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the task owner can view applicants",
            )

        applications = (
            self.db.query(Application)
            .filter(Application.task_id == task_id)
            .order_by(Application.created_at.desc())
            .all()
        )

        return [self._to_response(a) for a in applications]

    def update_application_status(
        self, application_id: str, new_status: str, owner_id: str
    ) -> ApplicationResponse:
        """
        Update the status of an application (accept/reject).
        Only the task owner can update application status.

        Args:
            application_id: UUID of the application.
            new_status: New status ('accepted' or 'rejected').
            owner_id: UUID of the requesting user (task owner).

        Returns:
            Updated ApplicationResponse.

        Raises:
            HTTPException: If application not found, invalid status, or not the owner.
        """
        if new_status not in ("accepted", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be 'accepted' or 'rejected'",
            )

        application = (
            self.db.query(Application)
            .filter(Application.id == application_id)
            .first()
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        # Verify the requester owns the task
        task = self.db.query(Task).filter(Task.id == application.task_id).first()
        if not task or task.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the task owner can update application status",
            )

        application.status = new_status
        self.db.commit()
        self.db.refresh(application)

        return self._to_response(application)

    def get_applications_by_applicant(self, applicant_id: str) -> List[ApplicationResponse]:
        """
        Get all applications submitted by a specific freelancer.

        Args:
            applicant_id: UUID of the freelancer.

        Returns:
            List of ApplicationResponse objects.
        """
        applications = (
            self.db.query(Application)
            .filter(Application.applicant_id == applicant_id)
            .order_by(Application.created_at.desc())
            .all()
        )
        return [self._to_response(a) for a in applications]

    def _to_response(self, application: Application) -> ApplicationResponse:
        """
        Convert an Application model to ApplicationResponse schema.
        Includes task title and applicant details.
        """
        return ApplicationResponse(
            id=application.id,
            task_id=application.task_id,
            task_title=application.task.title if application.task else None,
            applicant_id=application.applicant_id,
            applicant_name=application.applicant.name if application.applicant else None,
            applicant_skills=application.applicant.skills if application.applicant else None,
            cover_letter=application.cover_letter,
            status=application.status,
            created_at=application.created_at,
            updated_at=application.updated_at,
        )
