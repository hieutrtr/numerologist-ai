"""
Test configuration and fixtures.

Provides common fixtures for all tests including database sessions.
"""

import pytest
from sqlmodel import Session, SQLModel
from sqlalchemy import text
from src.core.database import engine


@pytest.fixture(scope="function")
def session():
    """
    Provide a transactional database session for tests.

    Creates a new session for each test and rolls back all changes
    after the test completes to maintain database isolation.
    """
    # Create tables (idempotent in test environment)
    SQLModel.metadata.create_all(engine)

    # Create a connection and start a transaction
    connection = engine.connect()
    transaction = connection.begin()

    # Create a session bound to the connection
    test_session = Session(bind=connection)

    yield test_session

    # Rollback the transaction to undo all test changes
    test_session.close()
    transaction.rollback()
    connection.close()
