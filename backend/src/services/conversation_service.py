"""
Conversation Service

Provides business logic for conversation management including:
- Retrieving recent conversations for context
- Caching conversation context in Redis
- Formatting conversation history for AI context
"""

import logging
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select
from src.models.conversation import Conversation
from src.core.database import engine
from src.core.redis import get_redis_client

logger = logging.getLogger(__name__)


async def get_recent_conversations(user_id: UUID, limit: int = 5) -> List[Dict]:
    """
    Retrieve recent completed conversations for a user.

    Queries the database for the user's most recent completed conversations
    (those with ended_at set) and extracts key information for context building.

    Args:
        user_id: UUID of the user whose conversations to retrieve
        limit: Maximum number of conversations to return (default: 5)

    Returns:
        List of conversation dictionaries with keys:
        - id: conversation UUID as string
        - date: started_at as ISO 8601 string
        - topic: main_topic or "General discussion"
        - insights: key_insights or empty string
        - numbers: numbers_discussed or empty string

    Example:
        conversations = await get_recent_conversations(user.id, limit=5)
        # Returns: [
        #   {
        #     "id": "uuid-string",
        #     "date": "2025-11-23T10:30:00Z",
        #     "topic": "Life Path Number",
        #     "insights": "User resonates with leadership qualities",
        #     "numbers": "1, 11"
        #   }
        # ]
    """
    try:
        with Session(engine) as session:
            # Query recent completed conversations
            statement = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .where(Conversation.ended_at.is_not(None))  # Only completed conversations
                .order_by(Conversation.started_at.desc())
                .limit(limit)
            )

            results = session.exec(statement).all()

            # Format for context
            summaries = []
            for conv in results:
                summaries.append({
                    "id": str(conv.id),
                    "date": conv.started_at.isoformat(),
                    "topic": conv.main_topic or "General discussion",
                    "insights": conv.key_insights or "",
                    "numbers": conv.numbers_discussed or ""
                })

            logger.info(
                f"Retrieved {len(summaries)} recent conversations for user {user_id}"
            )
            return summaries

    except Exception as e:
        logger.error(
            f"Error retrieving recent conversations for user {user_id}: {e}",
            exc_info=True
        )
        # Return empty list on error to prevent pipeline failure
        return []


async def get_conversation_context_cached(user_id: UUID) -> str:
    """
    Get conversation context with Redis caching.

    Implements cache-aside pattern:
    1. Check Redis cache for existing context
    2. If cache miss, compute context from database
    3. Store computed context in Redis with 30-minute TTL
    4. Return context string

    The context is formatted and ready to be injected into the system prompt.

    Args:
        user_id: UUID of the user whose context to retrieve

    Returns:
        Formatted conversation history string ready for system prompt.
        Returns empty string if user has no conversations or on error.

    Cache Details:
        - Key format: "context:{user_id}"
        - TTL: 1800 seconds (30 minutes)
        - Invalidation: Manual (when new conversation completes)

    Example:
        context = await get_conversation_context_cached(user.id)
        # Returns: "Previous conversations with this user:\\n1. Nov 23: Life Path Number..."
    """
    try:
        redis = get_redis_client()
        cache_key = f"context:{user_id}"

        # Check cache
        cached = redis.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for user {user_id} conversation context")
            return cached if isinstance(cached, str) else cached.decode('utf-8')

        # Cache miss - compute from database
        logger.debug(f"Cache miss for user {user_id} - computing context")

        # Import here to avoid circular dependency
        from src.voice_pipeline.system_prompts import format_conversation_history

        conversations = await get_recent_conversations(user_id, limit=5)
        context = format_conversation_history(conversations, max_tokens=500)

        # Store in cache with 30-minute TTL
        redis.set(cache_key, context, ex=1800)

        logger.info(
            f"Computed and cached conversation context for user {user_id} "
            f"({len(conversations)} conversations, {len(context)} chars)"
        )

        return context

    except Exception as e:
        logger.error(
            f"Error getting cached conversation context for user {user_id}: {e}",
            exc_info=True
        )
        # Return empty string on error to prevent pipeline failure
        return ""


async def invalidate_conversation_context_cache(user_id: UUID) -> None:
    """
    Invalidate cached conversation context for a user.

    Should be called when a new conversation is completed to ensure
    the next bot session loads fresh context.

    Args:
        user_id: UUID of the user whose cache to invalidate

    Example:
        # After ending a conversation
        await invalidate_conversation_context_cache(user.id)
    """
    try:
        redis = get_redis_client()
        cache_key = f"context:{user_id}"
        redis.delete(cache_key)
        logger.debug(f"Invalidated conversation context cache for user {user_id}")
    except Exception as e:
        logger.warning(
            f"Failed to invalidate cache for user {user_id}: {e}",
            exc_info=True
        )
        # Non-critical error - cache will expire naturally


__all__ = [
    "get_recent_conversations",
    "get_conversation_context_cached",
    "invalidate_conversation_context_cache",
]
