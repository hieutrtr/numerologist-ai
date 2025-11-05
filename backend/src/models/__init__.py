"""
Models Package

Imports all database models for SQLModel/Alembic auto-discovery.
This file must import all models to ensure Alembic can detect them
for automatic migration generation.
"""

from src.models.user import User

# Export all models
__all__ = ["User"]
