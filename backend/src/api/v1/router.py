"""
API v1 Router

Aggregates all v1 endpoints into a single router for inclusion in the main app.
"""

from fastapi import APIRouter

from src.api.v1.endpoints import auth, conversations


# Create v1 API router
api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include conversation endpoints
api_router.include_router(
    conversations.router,
    tags=["conversations"]
)
