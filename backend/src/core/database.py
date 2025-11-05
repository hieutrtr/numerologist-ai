"""
Database connection and session management for Numerologist AI.

This module provides SQLModel database connectivity with connection pooling
and dependency injection for FastAPI routes.
"""

import os
from typing import Generator

from sqlmodel import Session, create_engine


# Get database URL from environment with fallback to development database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/numerologist"
)

# Create SQLModel engine with connection pooling
# echo=True enables SQL query logging (useful for development)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is full
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency injection function for FastAPI routes.

    Provides a SQLModel Session that automatically commits on success
    and rolls back on exceptions. Should be used as a FastAPI Depends() parameter.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            users = session.exec(select(User)).all()
            return users
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
