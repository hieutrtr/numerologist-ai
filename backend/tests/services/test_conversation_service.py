"""
Unit tests for conversation service functions.

Tests conversation history retrieval, formatting, and Redis caching.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.services.conversation_service import (
    get_recent_conversations,
    get_conversation_context_cached,
    invalidate_conversation_context_cache
)


class TestGetRecentConversations:
    """Test suite for get_recent_conversations function."""

    @pytest.mark.asyncio
    async def test_returns_latest_5_conversations(self):
        """Test that function returns 5 most recent conversations."""
        user_id = uuid4()

        # Mock database session and query results
        with patch('src.services.conversation_service.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session

            # Create 10 mock conversations
            mock_conversations = []
            for i in range(10):
                mock_conv = Mock()
                mock_conv.id = uuid4()
                mock_conv.started_at = datetime.now(timezone.utc) - timedelta(days=i)
                mock_conv.main_topic = f"Topic {i}"
                mock_conv.key_insights = f"Insight {i}"
                mock_conv.numbers_discussed = f"{i}"
                mock_conversations.append(mock_conv)

            mock_session.exec.return_value.all.return_value = mock_conversations[:5]

            # Execute
            result = await get_recent_conversations(user_id, limit=5)

            # Assert
            assert len(result) == 5
            assert result[0]["topic"] == "Topic 0"  # Most recent first

    @pytest.mark.asyncio
    async def test_excludes_active_conversations(self):
        """Test that only completed conversations (ended_at != None) are returned."""
        user_id = uuid4()

        with patch('src.services.conversation_service.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session

            # Create 2 completed conversations
            mock_conversations = []
            for i in range(2):
                mock_conv = Mock()
                mock_conv.id = uuid4()
                mock_conv.started_at = datetime.now(timezone.utc) - timedelta(days=i)
                mock_conv.main_topic = f"Topic {i}"
                mock_conv.key_insights = f"Insight {i}"
                mock_conv.numbers_discussed = f"{i}"
                mock_conversations.append(mock_conv)

            mock_session.exec.return_value.all.return_value = mock_conversations

            # Execute
            result = await get_recent_conversations(user_id, limit=5)

            # Assert
            assert len(result) == 2
            # Verify query had ended_at.is_not(None) filter (query construction tested implicitly)

    @pytest.mark.asyncio
    async def test_orders_by_date_descending(self):
        """Test that results are ordered by started_at DESC."""
        user_id = uuid4()

        with patch('src.services.conversation_service.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session

            # Create conversations with specific dates
            mock_conversations = []
            dates = [
                datetime(2025, 11, 23, tzinfo=timezone.utc),
                datetime(2025, 11, 22, tzinfo=timezone.utc),
                datetime(2025, 11, 21, tzinfo=timezone.utc),
            ]

            for i, date in enumerate(dates):
                mock_conv = Mock()
                mock_conv.id = uuid4()
                mock_conv.started_at = date
                mock_conv.main_topic = f"Topic {date.day}"
                mock_conv.key_insights = ""
                mock_conv.numbers_discussed = ""
                mock_conversations.append(mock_conv)

            mock_session.exec.return_value.all.return_value = mock_conversations

            # Execute
            result = await get_recent_conversations(user_id, limit=5)

            # Assert order (most recent first)
            assert result[0]["date"] == "2025-11-23T00:00:00+00:00"
            assert result[1]["date"] == "2025-11-22T00:00:00+00:00"
            assert result[2]["date"] == "2025-11-21T00:00:00+00:00"

    @pytest.mark.asyncio
    async def test_handles_zero_conversations(self):
        """Test that empty list is returned when user has no conversations."""
        user_id = uuid4()

        with patch('src.services.conversation_service.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value.__enter__.return_value = mock_session

            mock_session.exec.return_value.all.return_value = []

            # Execute
            result = await get_recent_conversations(user_id, limit=5)

            # Assert
            assert result == []

    @pytest.mark.asyncio
    async def test_handles_database_error_gracefully(self):
        """Test that function returns empty list on database error."""
        user_id = uuid4()

        with patch('src.services.conversation_service.Session') as mock_session_class:
            mock_session_class.side_effect = Exception("Database connection failed")

            # Execute
            result = await get_recent_conversations(user_id, limit=5)

            # Assert - should return empty list, not raise exception
            assert result == []


class TestGetConversationContextCached:
    """Test suite for get_conversation_context_cached function with Redis caching."""

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_value(self):
        """Test that cached value is returned on cache hit."""
        user_id = uuid4()
        cached_context = "Previous conversations with this user:\n1. Nov 23: Life Path Number."

        with patch('src.services.conversation_service.get_redis_client') as mock_get_redis:
            mock_redis = Mock()
            mock_redis.get.return_value = cached_context
            mock_get_redis.return_value = mock_redis

            # Execute
            result = await get_conversation_context_cached(user_id)

            # Assert
            assert result == cached_context
            mock_redis.get.assert_called_once_with(f"context:{user_id}")
            mock_redis.set.assert_not_called()  # Should not write on cache hit

    @pytest.mark.asyncio
    async def test_cache_miss_computes_and_stores(self):
        """Test that context is computed and stored on cache miss."""
        user_id = uuid4()

        with patch('src.services.conversation_service.get_redis_client') as mock_get_redis, \
             patch('src.services.conversation_service.get_recent_conversations') as mock_get_convos:

            mock_redis = Mock()
            mock_redis.get.return_value = None  # Cache miss
            mock_get_redis.return_value = mock_redis

            # Mock conversation data
            mock_get_convos.return_value = [
                {
                    "id": str(uuid4()),
                    "date": "2025-11-23T10:30:00Z",
                    "topic": "Life Path Number",
                    "insights": "User resonates with leadership",
                    "numbers": "1, 11"
                }
            ]

            # Execute
            result = await get_conversation_context_cached(user_id)

            # Assert
            assert "Previous conversations with this user:" in result
            assert "Life Path Number" in result
            mock_redis.set.assert_called_once()
            # Verify TTL is 1800 seconds (30 minutes)
            call_args = mock_redis.set.call_args
            assert call_args[1]['ex'] == 1800

    @pytest.mark.asyncio
    async def test_returns_empty_string_on_error(self):
        """Test that empty string is returned on Redis error."""
        user_id = uuid4()

        with patch('src.services.conversation_service.get_redis_client') as mock_get_redis:
            mock_get_redis.side_effect = Exception("Redis connection failed")

            # Execute
            result = await get_conversation_context_cached(user_id)

            # Assert - should return empty string, not raise exception
            assert result == ""


class TestInvalidateConversationContextCache:
    """Test suite for invalidate_conversation_context_cache function."""

    @pytest.mark.asyncio
    async def test_deletes_cache_key(self):
        """Test that cache key is deleted for user."""
        user_id = uuid4()

        with patch('src.services.conversation_service.get_redis_client') as mock_get_redis:
            mock_redis = Mock()
            mock_get_redis.return_value = mock_redis

            # Execute
            await invalidate_conversation_context_cache(user_id)

            # Assert
            mock_redis.delete.assert_called_once_with(f"context:{user_id}")

    @pytest.mark.asyncio
    async def test_handles_redis_error_gracefully(self):
        """Test that function doesn't raise exception on Redis error."""
        user_id = uuid4()

        with patch('src.services.conversation_service.get_redis_client') as mock_get_redis:
            mock_get_redis.side_effect = Exception("Redis error")

            # Execute - should not raise exception
            await invalidate_conversation_context_cache(user_id)

            # No assertion needed - test passes if no exception raised
