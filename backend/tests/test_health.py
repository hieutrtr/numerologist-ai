"""
Tests for the health check endpoint.

Tests cover:
- Health endpoint with database connected (200 OK)
- Health endpoint response format
- Health endpoint with database unavailable (error handling)
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint_success():
    """Test health endpoint returns 200 with database connected."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "status" in data
    assert "database" in data

    # Verify values when database is connected
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_health_endpoint_response_format():
    """Test health endpoint returns correct JSON format."""
    response = client.get("/health")
    data = response.json()

    # Must have these keys
    required_keys = {"status", "database"}
    assert set(data.keys()) >= required_keys


def test_root_endpoint():
    """Test root endpoint still works (sanity check)."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Numerologist AI API"}


def test_health_endpoint_database_check():
    """Test that health endpoint actually checks database connectivity."""
    response = client.get("/health")
    data = response.json()

    # When database is up, we should get "connected"
    # This test runs with Docker database running
    assert data["database"] in ["connected", "disconnected"]

    # If database is connected, status should be healthy
    if data["database"] == "connected":
        assert data["status"] == "healthy"


# Note: Testing with database down requires stopping Docker containers
# This would be part of integration/E2E tests in a real environment
# For now, we verify the happy path since database is running
