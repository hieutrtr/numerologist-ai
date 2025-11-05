"""
Tests for dependency functions in src.core.deps module.

This module tests the authentication and authorization dependencies
used across API endpoints, particularly the get_current_user function
that validates JWT tokens and returns authenticated users.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from uuid import uuid4
from sqlmodel import Session, SQLModel

from src.main import app
from src.core.database import get_session, engine
from src.core.security import create_access_token
from src.models.user import User


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


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        birth_date=date(1990, 1, 15)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


class TestGetCurrentUserDependency:
    """
    Test suite for get_current_user dependency function.

    These tests verify the dependency works correctly when used
    via API endpoints. The dependency is tested indirectly through
    the GET /me endpoint which uses it.
    """

    def test_get_current_user_with_valid_token(self, client: TestClient, test_user: User):
        """
        Test get_current_user with valid JWT token returns User object.

        Verifies that a valid, non-expired token with correct user ID
        successfully returns the authenticated user from database.
        """
        # Arrange: Create valid token for test user
        token = create_access_token(data={"sub": str(test_user.id)})

        # Act: Call endpoint that uses get_current_user dependency
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: Returns correct user object via endpoint
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_current_user_with_invalid_token(self, client: TestClient):
        """
        Test get_current_user with invalid JWT token raises 401.

        Verifies that a malformed or incorrectly signed token
        results in 401 Unauthorized error.
        """
        # Arrange: Create invalid token (not properly signed)
        invalid_token = "invalid.jwt.token.string"

        # Act: Call endpoint with invalid token
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        # Assert: Returns 401 with error message
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_get_current_user_with_expired_token(self, client: TestClient, test_user: User):
        """
        Test get_current_user with expired JWT token raises 401.

        Verifies that a token past its expiration time is rejected
        with 401 Unauthorized error.
        """
        # Arrange: Create expired token (expired 1 minute ago)
        expired_token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(minutes=-1)  # Already expired
        )

        # Act: Call endpoint with expired token
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        # Assert: Returns 401
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_get_current_user_with_non_existent_user_id(self, client: TestClient):
        """
        Test get_current_user with valid token but non-existent user raises 401.

        Verifies that even with a valid token structure, if the user ID
        doesn't exist in database, 401 is raised with "User not found".
        """
        # Arrange: Create token with random UUID (user doesn't exist)
        non_existent_user_id = str(uuid4())
        token = create_access_token(data={"sub": non_existent_user_id})

        # Act: Call endpoint with token for non-existent user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: Returns 401 with "User not found"
        assert response.status_code == 401
        assert response.json()["detail"] == "User not found"

    def test_get_current_user_with_missing_sub_claim(self, client: TestClient):
        """
        Test get_current_user with token missing 'sub' claim raises 401.

        Verifies that a token without the required 'sub' (subject) claim
        is rejected with appropriate error message.
        """
        # Arrange: Create token without 'sub' claim
        token = create_access_token(data={"other_field": "value"})

        # Act: Call endpoint with token missing sub claim
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: Returns 401
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token payload"

    def test_get_current_user_token_structure_validation(self, client: TestClient, test_user: User):
        """
        Test get_current_user validates token structure correctly.

        Verifies that the dependency correctly extracts user ID from token
        payload and uses it for database lookup.
        """
        # Arrange: Create token with known user ID
        user_id_in_token = str(test_user.id)
        token = create_access_token(data={"sub": user_id_in_token})

        # Act: Get user via endpoint
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: User ID matches token payload
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id_in_token
        assert data["id"] == str(test_user.id)

    def test_get_current_user_with_inactive_user(self, client: TestClient, session: Session):
        """
        Test get_current_user with inactive user still returns user.

        Note: Current implementation doesn't check is_active flag.
        This test documents current behavior. Future stories may add
        active user validation.
        """
        # Arrange: Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            hashed_password="hashed_password",
            full_name="Inactive User",
            birth_date=date(1990, 1, 1),
            is_active=False
        )
        session.add(inactive_user)
        session.commit()
        session.refresh(inactive_user)

        # Create token for inactive user
        token = create_access_token(data={"sub": str(inactive_user.id)})

        # Act: Get user via endpoint
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: Returns inactive user (current behavior)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(inactive_user.id)
        assert data["is_active"] is False

        # Note: Future enhancement may add is_active check and return 401
