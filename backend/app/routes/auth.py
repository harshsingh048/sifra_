"""
Authentication Routes
=====================
Handles user registration, login, Google OAuth, and token refresh.

Endpoints:
    POST /api/auth/register  - Register a new user
    POST /api/auth/login     - Login with email/password
    POST /api/auth/google    - Login with Google OAuth
    POST /api/auth/refresh   - Refresh access token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import (
    GoogleLogin,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
Create a new user account with email and password.

**Roles:**
- `client` — Business owner looking to hire freelancers
- `freelancer` — Professional offering services

**Password Requirements:**
- Minimum 8 characters
- Must contain at least one letter and one number

**Example Request:**
```json
{
    "name": "Jane Smith",
    "email": "jane@bakery.com",
    "password": "SecurePass123!",
    "role": "client",
    "bio": "Owner of Jane's Artisan Bakery",
    "company_name": "Jane's Artisan Bakery"
}
```

**Example Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```
    """,
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **name**: Full name of the user
    - **email**: Unique email address
    - **password**: Secure password (min 8 chars)
    - **role**: 'client' or 'freelancer'
    - **bio**: Optional biography
    - **skills**: Optional skills (for freelancers)
    - **company_name**: Optional company name (for clients)
    """
    service = AuthService(db)
    return service.register(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="""
Authenticate with email and password to receive JWT tokens.

**Example Request:**
```json
{
    "email": "jane@bakery.com",
    "password": "SecurePass123!"
}
```

**Example Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```
    """,
)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns an access token (short-lived) and a refresh token (long-lived).
    Use the access token in the Authorization header for protected routes.
    """
    service = AuthService(db)
    return service.login(login_data)


@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Login with Google OAuth",
    description="""
Authenticate using a Google ID token obtained from the frontend Google Sign-In flow.

If the user doesn't exist, a new account is created automatically.

**Example Request:**
```json
{
    "google_token": "eyJhbGciOiJSUzI1NiIs...",
    "role": "freelancer"
}
```

**Example Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```
    """,
)
async def google_login(data: GoogleLogin, db: Session = Depends(get_db)):
    """
    Login or register via Google OAuth.

    - **google_token**: ID token from Google Sign-In
    - **role**: Role for new users ('client' or 'freelancer')
    """
    service = AuthService(db)
    return service.google_login(data.google_token, data.role)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="""
Use a valid refresh token to get a new access/refresh token pair.

**Example Request:**
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Example Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```
    """,
)
async def refresh_token(body: dict, db: Session = Depends(get_db)):
    """
    Refresh an expired access token.

    - **refresh_token**: Your current refresh token
    """
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required",
        )

    service = AuthService(db)
    return service.refresh_access_token(refresh_token)
