"""
OAuth Account Model

Defines the OAuthAccount database model for third-party authentication providers.
Stores OAuth provider information and tokens for users who sign in via Google, Apple, etc.
"""

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index, UniqueConstraint
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.user import User


class OAuthAccount(SQLModel, table=True):
    """
    OAuth Account model for third-party authentication.

    Stores OAuth provider information and tokens for users who authenticate via
    Google Sign-In, Apple Sign-In, or other OAuth providers.

    Features:
    - Each user can have multiple OAuth accounts (Google, Apple, etc.)
    - Foreign key to User with CASCADE delete
    - Unique constraint on (provider, provider_user_id) to prevent duplicates
    - Indexed on user_id for fast lookups
    - Tracks token expiration for future token refresh logic

    Example:
    - User signs in with Google
    - OAuthAccount created with provider='google', provider_user_id=<Google sub>
    - User can later link Apple OAuth to same account
    - User can still authenticate with email/password (if hashed_password set)
    """

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the OAuth account"
    )

    # Foreign key to User (CASCADE delete means OAuth account deleted when user deleted)
    user_id: UUID = Field(
        foreign_key="user.id",
        description="Foreign key to User table. Deletes this OAuth account when user is deleted."
    )

    # OAuth provider identification
    provider: str = Field(
        description="OAuth provider name (e.g., 'google', 'apple', 'microsoft')"
    )

    # Unique identifier from OAuth provider (e.g., Google's 'sub' claim)
    provider_user_id: str = Field(
        description="User's unique ID from the OAuth provider (e.g., Google's 'sub' claim)"
    )

    # Email from OAuth provider (may differ from User.email in edge cases)
    provider_email: str = Field(
        description="Email address from OAuth provider"
    )

    # OAuth tokens (nullable for flexibility, some providers may not return these)
    access_token: Optional[str] = Field(
        default=None,
        description="OAuth access token (nullable, used for future token refresh logic)"
    )

    refresh_token: Optional[str] = Field(
        default=None,
        description="OAuth refresh token (nullable, Google web flow doesn't return this)"
    )

    # Token expiration tracking
    token_expires_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when access token expires (nullable)"
    )

    # Metadata fields
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when OAuth account was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when OAuth account was last updated"
    )

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="oauth_accounts",
    )

    # Unique constraint: no duplicate OAuth accounts for same provider/user combo
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uc_oauth_account_provider_user_id"),
        Index("ix_oauth_account_user_id", "user_id"),
    )
