"""
Authentication Endpoints

API endpoints for user authentication operations including registration,
login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.core.database import get_session
from src.core.security import hash_password, create_access_token, verify_password
from src.models.user import User
from src.schemas.user import UserCreate, UserLogin, UserResponse


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
