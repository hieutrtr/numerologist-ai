"""
User Model

Defines the User database model for authentication and profile management.
This model stores core user information including authentication credentials
(hashed passwords) and personal information required for numerology calculations.
"""

from sqlmodel import SQLModel, Field
from datetime import date, datetime
from uuid import UUID, uuid4


class User(SQLModel, table=True):
    """
    User model for authentication and profile management.

    Stores user credentials, personal information, and account status.
    Passwords are NEVER stored in plain text - only bcrypt hashed values.
    Birth date is required for numerology calculations (Life Path, etc.).

    OAuth Support:
    - For OAuth users (Google/Apple sign-in), hashed_password will be NULL
    - OAuth authentication handled via separate OAuthAccount table (Story 2.11)

    Relationships (future stories):
    - numerology_profile: One-to-one with NumerologyProfile (Epic 4)
    - conversations: One-to-many with Conversation (Epic 3)
    - oauth_accounts: One-to-many with OAuthAccount (Story 2.11)
    """

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the user"
    )

    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        description="User's email address (unique, used for login)"
    )
    hashed_password: str | None = Field(
        default=None,
        description="Bcrypt hashed password (NEVER store plain text). NULL for OAuth users."
    )

    # Profile fields
    full_name: str = Field(
        description="User's full name for display"
    )
    birth_date: date = Field(
        description="User's birth date (required for numerology calculations)"
    )

    # Metadata fields
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user account was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when user account was last updated"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active (False = soft delete)"
    )
