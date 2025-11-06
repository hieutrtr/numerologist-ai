"""
Authentication Endpoints

API endpoints for user authentication operations including registration,
login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from uuid import UUID

from src.core.database import get_session
from src.core.security import hash_password, create_access_token, verify_password
from src.core.deps import get_current_user
from src.models.user import User
from src.models.oauth_account import OAuthAccount
from src.schemas.user import UserCreate, UserLogin, UserResponse, GoogleSignInRequest
from src.services.oauth_service import (
    verify_google_token,
    InvalidTokenError,
    TokenVerificationError,
    get_oauth_provider_user_id,
    get_oauth_user_email,
)


router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
) -> dict:
    """
    Register a new user account.

    Creates a new user with email, password, name, and birth date.
    Password is securely hashed before storage. Returns user data and JWT token.

    Args:
        user_data: User registration data (email, password, full_name, birth_date)
        session: Database session (dependency injection)

    Returns:
        dict: Response containing user data and access token
            {
                "user": UserResponse,
                "access_token": str,
                "token_type": "bearer"
            }

    Raises:
        HTTPException 400: Email already registered
        HTTPException 422: Validation error (invalid email, weak password, etc.)

    Security:
        - Password is hashed with bcrypt (cost factor 12) before storage
        - JWT token includes user ID in 'sub' claim
        - Token expires in 15 minutes (default)
        - Response excludes hashed_password for security

    Example Request:
        POST /api/v1/auth/register
        {
            "email": "user@example.com",
            "password": "securepass123",
            "full_name": "John Doe",
            "birth_date": "1990-01-15"
        }

    Example Response (201 Created):
        {
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "birth_date": "1990-01-15",
                "created_at": "2025-11-05T10:00:00",
                "updated_at": "2025-11-05T10:00:00",
                "is_active": true
            },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password using security utility from Story 2.2
    hashed_password = hash_password(user_data.password)

    # Create user instance
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        birth_date=user_data.birth_date
    )

    # Add to database
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create JWT access token with user ID in 'sub' claim
    access_token = create_access_token(data={"sub": str(user.id)})

    # Return user data (excluding hashed_password) and token
    return {
        "user": UserResponse.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin,
    session: Session = Depends(get_session)
) -> dict:
    """
    Authenticate user with email and password.

    Validates credentials against database and returns JWT token if successful.
    Uses case-insensitive email lookup and bcrypt password verification.

    Args:
        credentials: User login credentials (email, password)
        session: Database session (dependency injection)

    Returns:
        dict: Response containing user data and access token
            {
                "user": UserResponse,
                "access_token": str,
                "token_type": "bearer"
            }

    Raises:
        HTTPException 401: Invalid credentials (email not found or password incorrect)
        HTTPException 422: Validation error (invalid email format)

    Security:
        - Email lookup is case-insensitive
        - Password verification uses bcrypt constant-time comparison
        - Same error message for "user not found" and "wrong password" (prevents email enumeration)
        - JWT token includes user ID in 'sub' claim
        - Token expires in 15 minutes (default)
        - Response excludes hashed_password for security

    Example Request:
        POST /api/v1/auth/login
        {
            "email": "user@example.com",
            "password": "securepass123"
        }

    Example Response (200 OK):
        {
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "birth_date": "1990-01-15",
                "created_at": "2025-11-05T10:00:00",
                "updated_at": "2025-11-05T10:00:00",
                "is_active": true
            },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    Example Error Response (401 Unauthorized):
        {
            "detail": "Invalid credentials"
        }
    """
    # Query database for user by email (case-insensitive)
    user = session.exec(
        select(User).where(User.email.ilike(credentials.email))
    ).first()

    # If user not found, return 401 with generic message
    # (same message as wrong password to prevent email enumeration)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password using secure bcrypt comparison from Story 2.2
    if not verify_password(credentials.password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create JWT access token with user ID in 'sub' claim
    access_token = create_access_token(data={"sub": str(user.id)})

    # Return user data (excluding hashed_password) and token
    return {
        "user": UserResponse.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user profile.

    Returns the profile information for the currently authenticated user.
    Requires a valid JWT token in the Authorization header.

    This endpoint is protected by the get_current_user dependency, which:
    1. Validates the JWT token from Authorization header
    2. Verifies token signature and expiration
    3. Queries database for user by ID from token
    4. Returns 401 if token invalid, expired, or user not found

    Args:
        current_user: Authenticated user from get_current_user dependency.
                     Automatically injected by FastAPI dependency injection.

    Returns:
        UserResponse: User profile data (excludes hashed_password)
            {
                "id": UUID,
                "email": str,
                "full_name": str,
                "birth_date": date,
                "created_at": datetime,
                "updated_at": datetime,
                "is_active": bool
            }

    Raises:
        HTTPException: 401 Unauthorized in the following cases:
            - Authorization header missing
            - Token invalid or malformed
            - Token expired (after 15 minutes)
            - User not found in database

    Security:
        - Requires "Authorization: Bearer <token>" header
        - Token validation handled by get_current_user dependency
        - Response excludes sensitive data (hashed_password)
        - Same UserResponse schema as registration and login (consistency)

    Example Request:
        GET /api/v1/auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

    Example Response (200 OK):
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "full_name": "John Doe",
            "birth_date": "1990-01-15",
            "created_at": "2025-11-05T10:00:00",
            "updated_at": "2025-11-05T10:00:00",
            "is_active": true
        }

    Example Error Response (401 Unauthorized - Missing Token):
        {
            "detail": "Not authenticated"
        }

    Example Error Response (401 Unauthorized - Invalid Token):
        {
            "detail": "Invalid token"
        }

    Example Error Response (401 Unauthorized - User Not Found):
        {
            "detail": "User not found"
        }

    Usage Pattern:
        This endpoint demonstrates the standard pattern for protecting endpoints.
        Any future endpoint can be protected by adding the get_current_user dependency:

        ```python
        @router.get("/protected-resource")
        async def protected_route(current_user: User = Depends(get_current_user)):
            # Only authenticated users can access this
            return {"data": "sensitive information"}
        ```
    """
    return UserResponse.model_validate(current_user)


@router.post("/google", status_code=status.HTTP_200_OK)
async def google_sign_in(
    request: GoogleSignInRequest,
    session: Session = Depends(get_session)
) -> dict:
    """
    Authenticate user with Google OAuth ID token.

    Implements Google Sign-In flow for Android app. Frontend sends Google ID token,
    backend verifies it and either logs in existing user or creates new account.

    Handles three OAuth user linking cases:
    1. New user: Creates User + OAuthAccount
    2. Existing OAuth user: Returns existing user (prevents duplicates)
    3. Email match: Links OAuthAccount to existing password user

    Args:
        request: Google OAuth request with ID token
        session: Database session (dependency injection)

    Returns:
        dict: Same format as /login endpoint
            {
                "user": UserResponse,
                "access_token": str,
                "token_type": "bearer"
            }

    Raises:
        HTTPException 401: Invalid or expired Google ID token
        HTTPException 500: Token verification error (Google API issues)

    Security:
        - Verifies Google ID token signature on backend (prevents token forgery)
        - Uses GOOGLE_WEB_CLIENT_ID from environment for verification
        - Returns same JWT token format as /login and /register
        - For OAuth users, hashed_password is NULL
        - Prevents email enumeration (same approach as /login)

    Example Request:
        POST /api/v1/auth/google
        {
            "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI4YTQyMWNhZmZjZjc..."
        }

    Example Response (200 OK - New User):
        {
            "user": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@gmail.com",
                "full_name": "John Doe",
                "birth_date": null,  # Not provided by Google OAuth
                "created_at": "2025-11-06T15:30:00",
                "updated_at": "2025-11-06T15:30:00",
                "is_active": true
            },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    Example Response (200 OK - Existing User):
        {
            "user": { ... existing user data ... },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }

    Example Error Response (401 Unauthorized - Invalid Token):
        {
            "detail": "Invalid Google token: Token expired"
        }

    Flow Diagram:
        Frontend OAuth Flow:
        1. Frontend calls GoogleSignIn.signIn()
        2. User authenticates with Google
        3. Frontend receives ID token
        4. Frontend POST id_token to /api/v1/auth/google

        Backend Processing:
        5. Verify ID token signature with Google
        6. Extract user info (email, name, etc.)
        7. Query OAuthAccount by provider='google' + provider_user_id
           - If exists: Get user and return token (Case 2)
           - If not exists:
             - Query User by email
               - If exists: Create OAuthAccount link (Case 3)
               - If not exists: Create User + OAuthAccount (Case 1)
        8. Generate JWT token for user
        9. Return user + token
    """
    try:
        # Verify Google ID token and get user info
        user_info = verify_google_token(request.id_token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token verification failed"
        )

    # Extract user info from verified token
    provider_user_id = get_oauth_provider_user_id(user_info)
    provider_email = get_oauth_user_email(user_info)

    if not provider_user_id or not provider_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token: missing user ID or email"
        )

    # Case 2: Check if OAuth account already exists (prevent duplicates)
    existing_oauth = session.exec(
        select(OAuthAccount).where(
            (OAuthAccount.provider == "google") &
            (OAuthAccount.provider_user_id == provider_user_id)
        )
    ).first()

    if existing_oauth:
        # OAuth account exists, get associated user
        user = session.exec(
            select(User).where(User.id == existing_oauth.user_id)
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth account user not found"
            )

        # Update oauth_account last access time
        existing_oauth.updated_at = datetime.utcnow()
        session.add(existing_oauth)
        session.commit()

        access_token = create_access_token(data={"sub": str(user.id)})
        return {
            "user": UserResponse.model_validate(user),
            "access_token": access_token,
            "token_type": "bearer"
        }

    # Check if email matches existing user (Case 3 or Case 1)
    existing_user = session.exec(
        select(User).where(User.email.ilike(provider_email))
    ).first()

    if existing_user:
        # Case 3: Email match - link OAuth account to existing user
        oauth_account = OAuthAccount(
            user_id=existing_user.id,
            provider="google",
            provider_user_id=provider_user_id,
            provider_email=provider_email,
            access_token=None,  # Google doesn't return access_token for web apps
            refresh_token=None,
            token_expires_at=None,
        )
        session.add(oauth_account)
        session.commit()

        access_token = create_access_token(data={"sub": str(existing_user.id)})
        return {
            "user": UserResponse.model_validate(existing_user),
            "access_token": access_token,
            "token_type": "bearer"
        }

    # Case 1: New user - create User + OAuthAccount
    # Note: birth_date is required for User model but not provided by Google
    # Use a placeholder date (user must update profile later)
    from datetime import date
    placeholder_birth_date = date(2000, 1, 1)

    new_user = User(
        email=provider_email,
        hashed_password=None,  # OAuth user, no password
        full_name=user_info.get('name', 'Google User'),
        birth_date=placeholder_birth_date,
    )

    session.add(new_user)
    session.flush()  # Get the ID without committing

    # Create OAuth account for the new user
    oauth_account = OAuthAccount(
        user_id=new_user.id,
        provider="google",
        provider_user_id=provider_user_id,
        provider_email=provider_email,
        access_token=None,
        refresh_token=None,
        token_expires_at=None,
    )

    session.add(oauth_account)
    session.commit()
    session.refresh(new_user)

    # Create JWT access token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "user": UserResponse.model_validate(new_user),
        "access_token": access_token,
        "token_type": "bearer"
    }
