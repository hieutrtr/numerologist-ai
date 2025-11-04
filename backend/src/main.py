"""
Numerologist AI Backend - FastAPI Application

This is the main entry point for the Numerologist AI backend application.
It initializes the FastAPI app with CORS middleware and basic endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI application
app = FastAPI(
    title="Numerologist AI API",
    description="Backend API for Numerologist AI application - voice-based numerology readings",
    version="0.1.0",
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


@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Runs when the application starts up.
    """
    print("✓ Application startup - Numerologist AI API running")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Runs when the application is shutting down.
    """
    print("✓ Application shutdown")


# Health check endpoint (useful for monitoring)
@app.get("/health")
def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}
