"""
User Model
==========
Represents a user in the system (either a client/business or a freelancer).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration."""
    CLIENT = "client"
    FREELANCER = "freelancer"


class User(Base):
    """
    User table: stores both clients (business owners) and freelancers.

    Attributes:
        id: UUID primary key.
        name: Full name of the user.
        email: Unique email address (used for login).
        hashed_password: Bcrypt-hashed password.
        role: Either 'client' or 'freelancer'.
        bio: Optional biography / description.
        skills: Comma-separated list of skills (for freelancers).
        company_name: Optional company name (for clients).
        avatar_url: Optional profile picture URL.
        google_id: Google OAuth ID (if registered via Google).
        is_active: Whether the account is active.
        created_at: Account creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for Google OAuth users
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.FREELANCER)
    bio = Column(String(2000), nullable=True, default=None)
    skills = Column(String(1000), nullable=True, default=None)
    company_name = Column(String(255), nullable=True, default=None)
    avatar_url = Column(String(500), nullable=True, default=None)
    google_id = Column(String(255), unique=True, nullable=True, default=None)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    posted_tasks = relationship("Task", back_populates="owner", foreign_keys="Task.owner_id")
    applications = relationship("Application", back_populates="applicant")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
