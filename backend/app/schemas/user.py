"""
User Schemas
============
Pydantic models for user-related request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


# ─── Request Schemas ─────────────────────────────────────────────


class UserCreate(BaseModel):
    """
    Schema for user registration.

    Example:
    ```json
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "role": "client",
        "bio": "Small business owner looking for talented freelancers.",
        "company_name": "John's Bakery"
    }
    ```
    """

    name: str = Field(..., min_length=2, max_length=255, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address (unique)")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters, must contain letter and number)",
    )
    role: str = Field(
        ...,
        description="User role: 'client' (business owner) or 'freelancer'",
    )
    bio: Optional[str] = Field(None, max_length=2000, description="Short biography")
    skills: Optional[str] = Field(None, max_length=1000, description="Comma-separated skills (for freelancers)")
    company_name: Optional[str] = Field(None, max_length=255, description="Company name (for clients)")

    @validator("role")
    def validate_role(cls, v):
        if v not in ("client", "freelancer"):
            raise ValueError("Role must be either 'client' or 'freelancer'")
        return v

    @validator("password")
    def validate_password(cls, v):
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class UserLogin(BaseModel):
    """
    Schema for user login.

    Example:
    ```json
    {
        "email": "john@example.com",
        "password": "SecurePass123!"
    }
    ```
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class GoogleLogin(BaseModel):
    """
    Schema for Google OAuth login.

    Example:
    ```json
    {
        "google_token": "eyJhbGciOiJSUzI1NiIs..."
    }
    ```
    """

    google_token: str = Field(..., description="Google ID token from frontend OAuth flow")
    role: str = Field(
        "freelancer",
        description="User role for first-time registration: 'client' or 'freelancer'",
    )

    @validator("role")
    def validate_role(cls, v):
        if v not in ("client", "freelancer"):
            raise ValueError("Role must be either 'client' or 'freelancer'")
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional — only provided fields will be updated.

    Example:
    ```json
    {
        "name": "John Updated",
        "bio": "Updated bio text",
        "skills": "Python, JavaScript, React"
    }
    ```
    """

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    skills: Optional[str] = Field(None, max_length=1000)
    company_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)


# ─── Response Schemas ────────────────────────────────────────────


class TokenResponse(BaseModel):
    """
    JWT token response after successful login.

    Example:
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer"
    }
    ```
    """

    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="JWT refresh token (long-lived)")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """
    Public user profile response.
    Sensitive fields (password, etc.) are excluded.

    Example:
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "email": "john@example.com",
        "role": "client",
        "bio": "Small business owner",
        "skills": null,
        "company_name": "John's Bakery",
        "avatar_url": null,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
    }
    ```
    """

    id: str
    name: str
    email: str
    role: str
    bio: Optional[str]
    skills: Optional[str]
    company_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
