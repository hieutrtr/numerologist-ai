"""
Numerologist AI Backend - FastAPI Application

This is the main entry point for the Numerologist AI backend application.
It initializes the FastAPI app with CORS middleware and basic endpoints.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.

    Replaces deprecated @app.on_event() decorators with modern lifespan pattern.
    Runs startup code on entry, shutdown code on exit.

    Manages:
    - Database connection pool lifecycle
    - Future: Redis connection lifecycle
    """
    # Startup event
    from src.core.database import engine

    print("✓ Application startup - Numerologist AI API running")
    print("✓ Database connection pool initialized")

    yield

    # Shutdown event - cleanup resources
    print("✓ Disposing database connection pool...")
    engine.dispose()
    print("✓ Application shutdown complete")


# Initialize FastAPI application with lifespan
app = FastAPI(
    title="Numerologist AI API",
    description="Backend API for Numerologist AI application - voice-based numerology readings",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS middleware for mobile app integration
# In development, allow all origins. Will be restricted in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
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
@app.get("/health")
def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.

    Tests the database connection and returns comprehensive health status.

    Returns:
        dict: Health status with database connectivity information

    Example Response:
        {"status": "healthy", "database": "connected"}
    """
    from sqlmodel import Session, select, text
    from src.core.database import engine

    try:
        # Test database connection with a simple query
        with Session(engine) as session:
            # Execute a simple SELECT to verify connection
            session.exec(text("SELECT 1"))

        return {"status": "healthy", "database": "connected"}

    except Exception as e:
        # Log the error for debugging (in production, use proper logging)
        import logging
        logging.error(f"Database health check failed: {str(e)}")

        # Return error status
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": "Database connection failed"
        }
