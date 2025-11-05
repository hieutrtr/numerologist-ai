"""
Database connection and session management for Numerologist AI.

This module provides SQLModel database connectivity with connection pooling
and dependency injection for FastAPI routes.

Configuration is centralized in src.core.settings to avoid magic numbers
and scattered environment variable references.
"""

from typing import Generator

from sqlmodel import Session, create_engine

from .settings import settings


# Create SQLModel engine with connection pooling
# Configuration loaded from settings (environment variables or .env file)
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=settings.db_pool_pre_ping,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo_pool=settings.db_echo_pool,
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
