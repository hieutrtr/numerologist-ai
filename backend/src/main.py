"""
Numerologist AI Backend - FastAPI Application

This is the main entry point for the Numerologist AI backend application.
It initializes the FastAPI app with CORS middleware, health checks,
and manages lifecycle for database and cache connections.

Configuration is centralized in src.core.settings to avoid magic numbers
and scattered environment variable references.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.

    Replaces deprecated @app.on_event() decorators with modern lifespan pattern.
    Runs startup code on entry, shutdown code on exit.

    Manages:
    - Database (PostgreSQL) connection pool lifecycle
    - Redis connection pool and client lifecycle
    """
    # Startup event
    from src.core.database import engine
    from src.core.redis import get_redis_client

    print("✓ Application startup - Numerologist AI API running")
    print("✓ Database connection pool initialized")

    # Initialize Redis connection (validates connectivity)
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        print("✓ Redis connection pool initialized")
    except Exception as e:
        print(f"⚠ Redis initialization warning: {str(e)}")

    yield

    # Shutdown event - cleanup resources
    print("✓ Disposing database connection pool...")
    engine.dispose()

    print("✓ Disposing Redis connection pool...")
    from src.core.redis import dispose_redis_pool
    dispose_redis_pool()

    print("✓ Application shutdown complete")


# Initialize FastAPI application with lifespan and settings from configuration
app = FastAPI(
    title=settings.app_name,
    description="Backend API for Numerologist AI application - voice-based numerology readings",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_redoc else None,
)

# Configure CORS middleware for mobile app integration
# Configuration loaded from settings for flexibility across environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


@app.get("/")
def read_root() -> dict:
    """
    Root endpoint - returns basic API information.

    Returns:
        dict: API greeting message
    """
    return {"message": "Numerologist AI API"}


# Health check endpoint (useful for monitoring)
@app.get(settings.health_check_endpoint)
def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.

    Tests connectivity for all critical services:
    - PostgreSQL database
    - Redis cache/session store

    Returns:
        dict: Comprehensive health status with each service status

    Example Response:
        {
            "status": "healthy",
            "database": "connected",
            "redis": "connected"
        }
    """
    import logging
    from sqlmodel import Session, text

    from src.core.database import engine
    from src.core.redis import get_redis_client

    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "redis": "disconnected",
    }

    # Check database connection
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logging.error(f"Database health check failed: {str(e)}")
        health_status["status"] = "unhealthy"

    # Check Redis connection
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        logging.error(f"Redis health check failed: {str(e)}")
        health_status["status"] = "unhealthy"

    return health_status
