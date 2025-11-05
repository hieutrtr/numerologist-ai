"""
Dependency functions for FastAPI endpoints.

This module provides reusable dependency functions for request handling,
authentication, and authorization. These dependencies are injected into
endpoint functions to provide common functionality like user authentication.

Key Dependencies:
- get_current_user: Validates JWT token and returns authenticated user

Usage:
    from src.core.deps import get_current_user
    from src.models.user import User
    from fastapi import Depends

    @router.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        # current_user is automatically available and authenticated
        return {"message": f"Hello {current_user.full_name}"}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from src.core.security import verify_access_token
from src.core.database import get_session
from src.models.user import User


# HTTP Bearer authentication scheme for JWT tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Validate JWT token and return current authenticated user.

    This dependency function is used to protect endpoints that require authentication.
    It validates the JWT token from the Authorization header and returns the User object.

    The function performs the following steps:
    1. Extracts the JWT token from the Authorization header (via HTTPBearer)
    2. Verifies the token signature and expiration using verify_access_token()
    3. Extracts the user ID from the token payload ("sub" claim)
    4. Queries the database to retrieve the user by ID
    5. Returns the User object if all validations pass

    Args:
        credentials: HTTP Bearer token credentials from Authorization header.
                    Automatically extracted by FastAPI's HTTPBearer security scheme.
        session: Database session for querying user data.
                Injected via get_session dependency.

    Returns:
        User: The authenticated user object with all profile data.

    Raises:
        HTTPException: 401 Unauthorized in the following cases:
            - Token is missing from Authorization header (raised by HTTPBearer)
            - Token signature is invalid
            - Token has expired
            - Token payload is missing "sub" claim
            - User ID from token does not exist in database

    Example:
        ```python
        from fastapi import APIRouter, Depends
        from src.core.deps import get_current_user
        from src.models.user import User

        router = APIRouter()

        @router.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {
                "email": current_user.email,
                "name": current_user.full_name
            }

        @router.post("/numerology/calculate")
        async def calculate_numerology(
            birth_date: str,
            current_user: User = Depends(get_current_user)
        ):
            # Endpoint automatically protected - only authenticated users can access
            return {"user_id": current_user.id, "result": "..."}
        ```

    Security Notes:
        - This function is the primary authentication mechanism for protected endpoints
        - All protected endpoints should use this dependency to ensure user authentication
        - The HTTPBearer scheme requires "Authorization: Bearer <token>" header format
        - Tokens expire after 15 minutes (configured in security.py)
        - Failed authentication returns 401 before endpoint handler executes
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify token signature and expiration
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Extract user ID from token payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Query database for user by primary key (fast lookup)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
