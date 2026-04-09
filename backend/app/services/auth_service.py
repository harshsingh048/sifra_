"""
Authentication Service
======================
Handles user registration, login, token management, and Google OAuth.
"""

from datetime import timedelta
from typing import Optional

import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import TokenResponse, UserCreate, UserLogin


class AuthService:
    """
    Service class for all authentication-related operations.
    Separates business logic from route handlers for testability.
    """

    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserCreate) -> TokenResponse:
        """
        Register a new user with email/password.

        Steps:
        1. Check if email already exists.
        2. Hash the password.
        3. Create the user in the database.
        4. Generate JWT tokens.

        Args:
            user_data: Validated registration data.

        Returns:
            TokenResponse with access and refresh tokens.

        Raises:
            HTTPException: If email is already registered.
        """
        # Check for existing user
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered. Please login instead.",
            )

        # Create new user
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            role=UserRole(user_data.role),
            bio=user_data.bio,
            skills=user_data.skills,
            company_name=user_data.company_name,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        # Generate tokens
        return self._generate_tokens(new_user)

    def login(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user with email/password and return JWT tokens.

        Steps:
        1. Find user by email.
        2. Verify password.
        3. Check if account is active.
        4. Generate tokens.

        Args:
            login_data: Validated login credentials.

        Returns:
            TokenResponse with access and refresh tokens.

        Raises:
            HTTPException: If credentials are invalid.
        """
        # Find user
        user = self.db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not user.hashed_password or not verify_password(
            login_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check active status
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated. Contact support.",
            )

        return self._generate_tokens(user)

    def google_login(self, google_token: str, role: str) -> TokenResponse:
        """
        Authenticate or register a user via Google OAuth.

        Steps:
        1. Verify the Google ID token with Google's API.
        2. Extract user info from the token payload.
        3. If user exists, log them in.
        4. If new user, create account with Google info.
        5. Generate JWT tokens.

        Args:
            google_token: Google ID token from the frontend OAuth flow.
            role: User role for new registrations.

        Returns:
            TokenResponse with access and refresh tokens.

        Raises:
            HTTPException: If the Google token is invalid.
        """
        # Verify token with Google
        try:
            response = requests.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"
            )
            response.raise_for_status()
            google_data = response.json()
        except requests.RequestException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
            )

        google_id = google_data.get("sub")
        email = google_data.get("email")
        name = google_data.get("name", "Google User")
        picture = google_data.get("picture")

        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token payload",
            )

        # Check if user exists by Google ID or email
        user = (
            self.db.query(User)
            .filter((User.google_id == google_id) | (User.email == email))
            .first()
        )

        if user:
            # Existing user — update Google info if needed
            if not user.google_id:
                user.google_id = google_id
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated.",
                )
            self.db.commit()
        else:
            # New user — register via Google
            user = User(
                name=name,
                email=email,
                hashed_password=None,  # No password for OAuth users
                role=UserRole(role),
                google_id=google_id,
                avatar_url=picture,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        return self._generate_tokens(user)

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate a new access token using a valid refresh token.

        Steps:
        1. Decode and validate the refresh token.
        2. Verify it's actually a refresh token.
        3. Find the user.
        4. Generate new tokens.

        Args:
            refresh_token: The JWT refresh token.

        Returns:
            TokenResponse with new access and refresh tokens.

        Raises:
            HTTPException: If the refresh token is invalid.
        """
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Use a refresh token.",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> TokenResponse:
        """
        Internal helper to generate access and refresh tokens for a user.

        Args:
            user: The authenticated User object.

        Returns:
            TokenResponse containing both tokens.
        """
        token_data = {"sub": user.id, "role": user.role}

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = create_refresh_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
