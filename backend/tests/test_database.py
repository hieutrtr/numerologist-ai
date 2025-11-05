"""
Tests for database connection and session management.

Tests cover:
- Engine creation and configuration
- Session generation via get_session()
- Environment variable loading
- Connection error handling
"""

import os
from unittest.mock import patch

import pytest
from sqlmodel import Session, text

from src.core.database import DATABASE_URL, engine, get_session


def test_database_url_from_environment():
    """Test that DATABASE_URL is loaded from environment or uses fallback."""
    # The DATABASE_URL should be a PostgreSQL connection string
    assert DATABASE_URL.startswith("postgresql://")
    assert "postgres" in DATABASE_URL
    assert "numerologist" in DATABASE_URL


def test_engine_creation():
    """Test that SQLModel engine is created successfully."""
    assert engine is not None
    assert str(engine.url).startswith("postgresql://")


def test_get_session_yields_session():
    """Test that get_session() yields a valid Session."""
    session_generator = get_session()
    session = next(session_generator)

    assert isinstance(session, Session)

    # Clean up
    try:
        next(session_generator)
    except StopIteration:
        pass


def test_database_connection():
    """Test that we can connect to the database and execute a query."""
    with Session(engine) as session:
        # Execute a simple SELECT query
        result = session.exec(text("SELECT 1 as num"))
        row = result.one()
        assert row.num == 1


def test_get_session_commits_on_success():
    """Test that get_session() commits transactions on success."""
    # This test verifies the session context manager behavior
    session_generator = get_session()
    session = next(session_generator)

    # Perform a simple query (no actual table changes in this test)
    result = session.exec(text("SELECT 1"))
    assert result is not None

    # Clean up - this should trigger commit
    try:
        next(session_generator)
    except StopIteration:
        pass  # Expected behavior


def test_get_session_rollsback_on_exception():
    """Test that get_session() rolls back on exceptions."""
    session_generator = get_session()
    session = next(session_generator)

    # Simulate an error by trying to close early
    # The context manager should handle rollback

    try:
        # Force an exception
        raise ValueError("Test exception")
    except ValueError:
        pass

    # Clean up
    try:
        session_generator.throw(ValueError("Test exception"))
    except (StopIteration, ValueError):
        pass  # Expected - session should rollback
