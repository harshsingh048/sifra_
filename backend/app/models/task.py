"""
Task Model
==========
Represents a freelance task/post created by a client.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    """
    Task table: freelance posts created by clients.

    Attributes:
        id: UUID primary key.
        title: Task title.
        description: Detailed task description.
        budget: Budget amount for the task.
        location: Physical or remote location.
        status: 'open', 'in_progress', 'completed', 'cancelled'.
        owner_id: UUID of the client who posted the task.
        created_at: Task creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Float, nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="open")
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="posted_tasks", foreign_keys=[owner_id])
    applications = relationship("Application", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, budget={self.budget})>"
