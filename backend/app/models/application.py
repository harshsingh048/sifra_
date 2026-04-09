"""
Application Model
=================
Represents a freelancer's application to a task.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Application(Base):
    """
    Application table: freelancer applications to tasks.

    Attributes:
        id: UUID primary key.
        task_id: UUID of the task being applied to.
        applicant_id: UUID of the freelancer applying.
        cover_letter: Application message / cover letter.
        status: 'pending', 'accepted', 'rejected'.
        created_at: Application creation timestamp.
        updated_at: Last update timestamp.

    Constraints:
        Unique constraint on (task_id, applicant_id) to prevent duplicate applications.
    """

    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    applicant_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    task = relationship("Task", back_populates="applications")
    applicant = relationship("User", back_populates="applications")

    # Prevent duplicate applications to the same task
    __table_args__ = (
        UniqueConstraint("task_id", "applicant_id", name="uq_task_applicant"),
    )

    def __repr__(self) -> str:
        return f"<Application(id={self.id}, task={self.task_id}, applicant={self.applicant_id})>"
