"""
Application settings and configuration management.

Centralizes all configuration using Pydantic Settings to avoid magic numbers,
hardcoding, and scattered environment variable references.

Configuration is loaded from environment variables with sensible defaults for
local development. Override via environment variables in production.

Usage:
    from src.core.settings import settings

    db_url = settings.database_url
    redis_url = settings.redis_url
    pool_size = settings.db_pool_size
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables. For example:
    - export DATABASE_URL="postgresql://user:pass@host:5432/db"
    - export REDIS_URL="redis://localhost:6379"
    - export DEBUG=true
    """

    # =====================================================================
    # APPLICATION
    # =====================================================================
    app_name: str = "Numerologist AI API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # =====================================================================
    # DATABASE (PostgreSQL)
    # =====================================================================
    database_url: str = (
        "postgresql://postgres:password@localhost:5432/numerologist"
    )
    """
    PostgreSQL connection string.

    Format: postgresql://user:password@host:port/database
    Environment variable: DATABASE_URL
    """

    db_echo: bool = False
    """Enable SQL query logging. Set to True for debugging."""

    db_pool_size: int = 5
    """
    Number of connections to maintain in the pool.

    Recommended values:
    - Development: 5
    - Staging: 10
    - Production: 20-50 (depending on concurrency)
    """

    db_max_overflow: int = 10
    """
    Maximum overflow connections beyond pool_size.

    When pool is full, additional connections up to this limit are created.
    Recommended: 2-3x pool_size
    """

    db_pool_pre_ping: bool = True
    """
    Verify connections before using them.

    Detects connections that have been closed or invalidated.
    Prevents "connection reset by peer" errors.
    """

    db_echo_pool: bool = False
    """Enable connection pool logging. Useful for debugging connection issues."""

    # =====================================================================
    # REDIS (Cache & Session Store)
    # =====================================================================
    redis_url: str = "redis://localhost:6379"
    """
    Redis connection string.

    Format: redis://[:password]@host:port/db
    Environment variable: REDIS_URL

    Examples:
    - Local: redis://localhost:6379
    - With password: redis://:password@host:6379
    - With database: redis://localhost:6379/1
    """

    redis_pool_size: int = 10
    """
    Maximum number of connections in Redis connection pool.

    Recommended values:
    - Development: 5-10
    - Production: 20-50
    """

    redis_pool_timeout: int = 30
    """Timeout in seconds for acquiring a connection from Redis pool."""

    redis_socket_keepalive: bool = True
    """Enable TCP keepalive for Redis connections."""

    redis_socket_keepalive_options: dict = {
        "TCP_KEEPIDLE": 60,
        "TCP_KEEPINTVL": 10,
        "TCP_KEEPCNT": 5,
    }
    """TCP keepalive socket options for Redis connections."""

    # =====================================================================
    # CORS & SECURITY
    # =====================================================================
    cors_origins: list[str] = ["*"]
    """
    Allowed CORS origins.

    Development: ["*"] allows all
    Production: Should be specific domains only
    """

    cors_allow_credentials: bool = True
    """Allow cookies/credentials in CORS requests."""

    cors_allow_methods: list[str] = ["*"]
    """Allowed HTTP methods for CORS."""

    cors_allow_headers: list[str] = ["*"]
    """Allowed headers for CORS."""

    # =====================================================================
    # API ENDPOINTS
    # =====================================================================
    api_prefix: str = "/api"
    """Prefix for API routes. Example: /api/v1"""

    health_check_endpoint: str = "/health"
    """Health check endpoint path."""

    # =====================================================================
    # LOGGING & MONITORING
    # =====================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """Logging level."""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    """Logging format string."""

    # =====================================================================
    # TIMEOUTS & LIMITS
    # =====================================================================
    request_timeout: int = 30
    """Request timeout in seconds."""

    max_connection_attempts: int = 3
    """Maximum database connection retry attempts."""

    connection_retry_delay: float = 1.0
    """Delay in seconds between connection retry attempts."""

    # =====================================================================
    # FEATURE FLAGS
    # =====================================================================
    enable_docs: bool = True
    """Enable Swagger documentation (/docs endpoint)."""

    enable_redoc: bool = True
    """Enable ReDoc documentation (/redoc endpoint)."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()

__all__ = ["Settings", "settings"]
