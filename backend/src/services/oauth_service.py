"""
OAuth Service - Third-party authentication verification

Provides services for verifying OAuth tokens from providers like Google,
and managing OAuth account linking and authentication.
"""

import logging
from typing import Dict, Any, Optional
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from src.core.settings import settings

logger = logging.getLogger(__name__)


class OAuthServiceError(Exception):
    """Base exception for OAuth service errors."""
    pass


class InvalidTokenError(OAuthServiceError):
    """Raised when an OAuth token is invalid or expired."""
    pass


class TokenVerificationError(OAuthServiceError):
    """Raised when token verification fails."""
    pass


def verify_google_token(id_token_str: str) -> Dict[str, Any]:
    """
    Verify a Google OAuth ID token and return user information.

    This function verifies that:
    - Token signature is valid (signed by Google)
    - Token is not expired
    - Token audience matches our client ID

    Args:
        id_token_str: Google ID token string (JWT) from frontend

    Returns:
        Dictionary containing user info:
        {
            'sub': 'unique_google_user_id',
            'email': 'user@example.com',
            'name': 'User Name',
            'picture': 'https://...',  # Optional
            'email_verified': True,
        }

    Raises:
        ValueError: If token is invalid, expired, or verification fails
        TokenVerificationError: If Google API verification fails
        InvalidTokenError: If token format is invalid

    Example:
        try:
            user_info = verify_google_token(id_token)
            email = user_info['email']
            google_user_id = user_info['sub']
        except InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise
    """
    if not id_token_str:
        raise InvalidTokenError("ID token is required")

    if not settings.google_web_client_id:
        logger.error("GOOGLE_WEB_CLIENT_ID not configured")
        raise TokenVerificationError("Google OAuth not configured on server")

    try:
        # Verify token signature and get claims
        # Using google.oauth2.id_token.verify_oauth2_token
        # This checks:
        # - Token signature (verify against Google's public keys)
        # - Token expiration
        # - Token audience (client ID)
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            cid=settings.google_web_client_id,
        )

        # If token was issued by Google and not modified, idinfo is valid
        logger.info(f"Google token verified for user {idinfo.get('email')}")

        # Return essential user info from token claims
        return {
            'sub': idinfo['sub'],  # Google's unique user ID
            'email': idinfo.get('email', ''),
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False),
        }

    except ValueError as e:
        # ValueError raised by google.oauth2.id_token.verify_oauth2_token
        # Covers: invalid token, wrong audience, expired token, bad signature
        error_msg = str(e)
        logger.warning(f"Invalid Google token: {error_msg}")

        if "Token expired" in error_msg or "exp" in error_msg:
            raise InvalidTokenError("Google token has expired")
        elif "audience" in error_msg.lower() or "cid" in error_msg.lower():
            raise InvalidTokenError("Google token audience mismatch")
        else:
            raise InvalidTokenError(f"Invalid Google token: {error_msg}")

    except Exception as e:
        # Catch any other errors (network issues, Google API problems, etc.)
        logger.error(f"Google token verification error: {type(e).__name__}: {e}")
        raise TokenVerificationError(f"Token verification failed: {str(e)}")


def get_oauth_provider_user_id(user_info: Dict[str, Any]) -> str:
    """
    Extract OAuth provider's unique user ID from verified user info.

    This is used as the unique identifier in OAuthAccount table.

    Args:
        user_info: Verified user information dict

    Returns:
        Provider's unique user ID (e.g., Google's 'sub' claim)
    """
    return user_info.get('sub', '')


def get_oauth_user_email(user_info: Dict[str, Any]) -> str:
    """
    Extract user email from verified user info.

    Args:
        user_info: Verified user information dict

    Returns:
        User's email address
    """
    return user_info.get('email', '')


__all__ = [
    "verify_google_token",
    "get_oauth_provider_user_id",
    "get_oauth_user_email",
    "OAuthServiceError",
    "InvalidTokenError",
    "TokenVerificationError",
]
