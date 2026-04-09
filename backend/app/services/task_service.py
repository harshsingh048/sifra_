"""
Task Service
============
Handles task/post CRUD operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.application import Application
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    """
    Service class for task-related operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: TaskCreate, owner_id: str) -> TaskResponse:
        """
        Create a new task/post.
        Only clients can create tasks.

        Args:
            task_data: Validated task creation data.
            owner_id: UUID of the client creating the task.

        Returns:
            TaskResponse with the created task details.
        """
        task = Task(
            title=task_data.title,
            description=task_data.description,
            budget=task_data.budget,
            location=task_data.location,
            owner_id=owner_id,
            status="open",
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return self._to_response(task)

    def get_all_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
        location: Optional[str] = None,
        min_budget: Optional[float] = None,
        max_budget: Optional[float] = None,
        search: Optional[str] = None,
    ) -> List[TaskResponse]:
        """
        Get all tasks with filtering, searching, and pagination.

        Args:
            skip: Pagination offset.
            limit: Maximum results.
            status_filter: Filter by status (open, in_progress, completed, cancelled).
            location: Filter by location.
            min_budget: Minimum budget filter.
            max_budget: Maximum budget filter.
            search: Full-text search in title and description.

        Returns:
            List of TaskResponse objects.
        """
        query = self.db.query(Task)

        # Apply filters
        if status_filter:
            query = query.filter(Task.status == status_filter)
        if location:
            query = query.filter(Task.location.ilike(f"%{location}%"))
        if min_budget is not None:
            query = query.filter(Task.budget >= min_budget)
        if max_budget is not None:
            query = query.filter(Task.budget <= max_budget)
        if search:
            query = query.filter(
                Task.title.ilike(f"%{search}%")
                | Task.description.ilike(f"%{search}%")
            )

        # Order by newest first
        query = query.order_by(Task.created_at.desc())

        tasks = query.offset(skip).limit(limit).all()
        return [self._to_response(t) for t in tasks]

    def get_task_by_id(self, task_id: str) -> TaskResponse:
        """
        Get a single task by ID.

        Args:
            task_id: UUID of the task.

        Returns:
            TaskResponse with task details and application count.

        Raises:
            HTTPException: If task not found.
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return self._to_response(task)

    def update_task(
        self, task_id: str, owner_id: str, update_data: TaskUpdate
    ) -> TaskResponse:
        """
        Update a task. Only the owner can update.

        Args:
            task_id: UUID of the task.
            owner_id: UUID of the requesting user.
            update_data: Fields to update.

        Returns:
            Updated TaskResponse.

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
                detail="You can only update your own tasks",
            )

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)

        return self._to_response(task)

    def delete_task(self, task_id: str, owner_id: str) -> dict:
        """
        Delete a task. Only the owner can delete.
        Also deletes all associated applications (cascade).

        Args:
            task_id: UUID of the task.
            owner_id: UUID of the requesting user.

        Returns:
            Success message.

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
                detail="You can only delete your own tasks",
            )

        self.db.delete(task)
        self.db.commit()

        return {"message": "Task deleted successfully"}

    def get_tasks_by_owner(self, owner_id: str) -> List[TaskResponse]:
        """
        Get all tasks posted by a specific user.

        Args:
            owner_id: UUID of the task owner.

        Returns:
            List of TaskResponse objects.
        """
        tasks = (
            self.db.query(Task)
            .filter(Task.owner_id == owner_id)
            .order_by(Task.created_at.desc())
            .all()
        )
        return [self._to_response(t) for t in tasks]

    def _to_response(self, task: Task) -> TaskResponse:
        """
        Convert a Task model to TaskResponse schema.
        Includes owner name and application count.
        """
        # Count applications
        app_count = (
            self.db.query(func.count(Application.id))
            .filter(Application.task_id == task.id)
            .scalar()
        )

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            budget=task.budget,
            location=task.location,
            status=task.status,
            owner_id=task.owner_id,
            owner_name=task.owner.name if task.owner else None,
            application_count=app_count or 0,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
