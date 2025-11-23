"""
Models Package

Imports all database models for SQLModel/Alembic auto-discovery.
This file must import all models to ensure Alembic can detect them
for automatic migration generation.
"""

from src.models.user import User
from src.models.oauth_account import OAuthAccount
from src.models.conversation import Conversation
from src.models.conversation_message import ConversationMessage

# Export all models
__all__ = ["User", "OAuthAccount", "Conversation", "ConversationMessage"]
