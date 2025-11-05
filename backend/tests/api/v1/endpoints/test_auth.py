"""
Authentication Endpoint Tests

Comprehensive test suite for user registration and authentication endpoints.
Tests validation, error handling, security, and response formats.
"""

import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.main import app
from src.models.user import User
from src.core.database import get_session, engine
from src.core.security import verify_access_token
from sqlmodel import SQLModel


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a fresh database session for each test.

    Drops all tables and recreates them to ensure test isolation.
    """
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a FastAPI TestClient with test database session.

    Overrides the get_session dependency to use the test session.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestUserRegistration:
    """Test suite for user registration endpoint."""

    def test_register_with_valid_data(self, client: TestClient, session: Session):
        """
        Test successful user registration with valid data.

        Verifies:
        - 201 status code
        - User data in response
        - JWT token present
        - Token type is 'bearer'
        - User created in database
        """
        # Arrange
        registration_data = {
            "email": "testuser@example.com",
            "password": "securepass123",
            "full_name": "Test User",
            "birth_date": "1990-01-15"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "user" in data
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # Check user data
        user_data = data["user"]
        assert user_data["email"] == registration_data["email"]
        assert user_data["full_name"] == registration_data["full_name"]
        assert user_data["birth_date"] == registration_data["birth_date"]
        assert "id" in user_data
        assert "created_at" in user_data
        assert "updated_at" in user_data
        assert user_data["is_active"] is True

        # Verify user exists in database
        user = session.exec(
            select(User).where(User.email == registration_data["email"])
        ).first()
        assert user is not None
        assert user.email == registration_data["email"]

    def test_register_duplicate_email(self, client: TestClient, session: Session):
        """
        Test registration with duplicate email returns 400 error.

        Verifies:
        - 400 status code
        - Error message about duplicate email
        """
        # Arrange - Create first user
        registration_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "First User",
            "birth_date": "1990-01-15"
        }
        client.post("/api/v1/auth/register", json=registration_data)

        # Act - Try to register with same email
        response = client.post("/api/v1/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """
        Test registration with invalid email format returns 422 validation error.

        Verifies:
        - 422 status code
        - Validation error for email field
        """
        # Arrange
        invalid_data = {
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Test User",
            "birth_date": "1990-01-15"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=invalid_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(error["loc"] == ["body", "email"] for error in errors)

    def test_register_weak_password(self, client: TestClient):
        """
        Test registration with weak password (< 8 chars) returns 422 error.

        Verifies:
        - 422 status code
        - Validation error for password field
        """
        # Arrange
        weak_password_data = {
            "email": "user@example.com",
            "password": "short",  # Only 5 characters
            "full_name": "Test User",
            "birth_date": "1990-01-15"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=weak_password_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(error["loc"] == ["body", "password"] for error in errors)

    def test_register_future_birth_date(self, client: TestClient):
        """
        Test registration with future birth date returns 422 validation error.

        Verifies:
        - 422 status code
        - Validation error for birth_date field
        """
        # Arrange
        future_date = (date.today() + timedelta(days=1)).isoformat()
        future_birth_data = {
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User",
            "birth_date": future_date
        }

        # Act
        response = client.post("/api/v1/auth/register", json=future_birth_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(error["loc"] == ["body", "birth_date"] for error in errors)

    def test_register_birth_date_today(self, client: TestClient):
        """
        Test registration with birth date equal to today returns validation error.

        Birth date must be in the past (not today, not future).

        Verifies:
        - 422 status code
        - Validation error for birth_date field
        """
        # Arrange
        today = date.today().isoformat()
        today_birth_data = {
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User",
            "birth_date": today
        }

        # Act
        response = client.post("/api/v1/auth/register", json=today_birth_data)

        # Assert
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(error["loc"] == ["body", "birth_date"] for error in errors)

    def test_register_missing_required_fields(self, client: TestClient):
        """
        Test registration with missing required fields returns 422 error.

        Verifies:
        - 422 status code when email is missing
        - 422 status code when password is missing
        - 422 status code when full_name is missing
        - 422 status code when birth_date is missing
        """
        # Test missing email
        response = client.post("/api/v1/auth/register", json={
            "password": "password123",
            "full_name": "Test User",
            "birth_date": "1990-01-15"
        })
        assert response.status_code == 422

        # Test missing password
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "full_name": "Test User",
            "birth_date": "1990-01-15"
        })
        assert response.status_code == 422

        # Test missing full_name
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "birth_date": "1990-01-15"
        })
        assert response.status_code == 422

        # Test missing birth_date
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        assert response.status_code == 422

    def test_register_password_is_hashed(self, client: TestClient, session: Session):
        """
        Test that password is hashed in database (not stored as plain text).

        Verifies:
        - hashed_password in database does not match plain password
        - hashed_password starts with bcrypt identifier ($2b$)
        """
        # Arrange
        plain_password = "myplainpassword"
        registration_data = {
            "email": "hashtest@example.com",
            "password": plain_password,
            "full_name": "Hash Test",
            "birth_date": "1990-01-15"
        }

        # Act
        client.post("/api/v1/auth/register", json=registration_data)

        # Assert
        user = session.exec(
            select(User).where(User.email == registration_data["email"])
        ).first()
        assert user is not None
        assert user.hashed_password != plain_password  # Not stored as plain text
        assert user.hashed_password.startswith("$2b$")  # Bcrypt hash format

    def test_register_response_excludes_password(self, client: TestClient):
        """
        Test that API response does not include hashed_password field.

        Verifies:
        - Response JSON does not contain 'hashed_password' key
        - Response JSON does not contain 'password' key
        - Security: prevents accidental password exposure
        """
        # Arrange
        registration_data = {
            "email": "security@example.com",
            "password": "securepass123",
            "full_name": "Security Test",
            "birth_date": "1990-01-15"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        user_data = data["user"]

        # Ensure no password fields in response
        assert "password" not in user_data
        assert "hashed_password" not in user_data

    def test_register_token_is_valid(self, client: TestClient):
        """
        Test that JWT token in response is valid and contains user ID.

        Verifies:
        - Token can be successfully decoded
        - Token contains 'sub' claim with user ID
        - Token expiration is set
        """
        # Arrange
        registration_data = {
            "email": "tokentest@example.com",
            "password": "password123",
            "full_name": "Token Test",
            "birth_date": "1990-01-15"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=registration_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        token = data["access_token"]

        # Verify token can be decoded
        payload = verify_access_token(token)
        assert payload is not None
        assert "sub" in payload  # User ID in 'sub' claim
        assert "exp" in payload  # Expiration time set

        # Verify user ID matches
        user_id_from_token = payload["sub"]
        user_id_from_response = data["user"]["id"]
        assert user_id_from_token == user_id_from_response

    def test_register_special_characters_in_email(self, client: TestClient):
        """
        Test registration with valid email containing special characters.

        RFC 5322 allows various special characters in email addresses.
        Common valid formats: user+tag@example.com, user.name@example.com

        Verifies:
        - 201 status code for valid special character emails
        - User successfully created
        """
        # Arrange - Email with + symbol (common for email filtering)
        special_email_data = {
            "email": "user+test@example.com",
            "password": "password123",
            "full_name": "Special Email Test",
            "birth_date": "1990-01-15"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=special_email_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == special_email_data["email"]
