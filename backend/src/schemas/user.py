"""
User Pydantic Schemas

Request and response schemas for user-related API endpoints.
These schemas define validation rules and response structures for user operations.
"""

from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class UserCreate(BaseModel):
    """
    Schema for user registration request.

    Validates user input for account creation including email format,
    password strength, and birth date validity.

    Attributes:
        email: User's email address (validated format)
        password: Plain text password (min 8 characters)
        full_name: User's full name for display
        birth_date: User's birth date for numerology calculations

    Example:
        {
            "email": "user@example.com",
            "password": "securepass123",
            "full_name": "John Doe",
            "birth_date": "1990-01-15"
        }
    """

    email: EmailStr = Field(
        ...,
        description="User's email address (must be valid format)"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)"
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name"
    )
    birth_date: date = Field(
        ...,
        description="User's birth date (required for numerology, must be in past)"
    )

    @field_validator('birth_date')
    @classmethod
    def birth_date_must_be_in_past(cls, v: date) -> date:
        """
        Validate that birth date is not in the future.

        Users must provide a birth date that is in the past (not today, not future).
        This is required for numerology calculations and prevents invalid data.

        Args:
            v: The birth date value to validate

        Returns:
            date: The validated birth date

        Raises:
            ValueError: If birth date is today or in the future
        """
        from datetime import date as date_module
        today = date_module.today()

        if v >= today:
            raise ValueError('Birth date must be in the past')

        return v


class UserLogin(BaseModel):
    """
    Schema for user login request.

    Accepts email and password for authentication.
    Validation of credentials against the database is performed in the endpoint,
    not at the schema level.

    Attributes:
        email: User's email address (validated format)
        password: User's plain text password

    Example:
        {
            "email": "user@example.com",
            "password": "securepass123"
        }
    """

    email: EmailStr = Field(
        ...,
        description="User's email address (must be valid format)"
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Password (authenticated against hashed password in database)"
    )


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.

    Represents user information returned by the API, excluding sensitive fields
    like hashed_password for security.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address
        full_name: User's full name
        birth_date: User's birth date
        created_at: Account creation timestamp
        updated_at: Last profile update timestamp
        is_active: Whether the account is active

    Security Note:
        This schema intentionally EXCLUDES hashed_password to prevent
        accidental exposure of password hashes in API responses.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "full_name": "John Doe",
            "birth_date": "1990-01-15",
            "created_at": "2025-11-05T10:00:00",
            "updated_at": "2025-11-05T10:00:00",
            "is_active": true
        }
    """

    id: UUID = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    birth_date: date = Field(..., description="User's birth date")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(default=True, description="Account active status")

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for SQLModel compatibility
