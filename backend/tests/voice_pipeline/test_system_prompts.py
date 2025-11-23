"""
Unit tests for system prompt generation, token counting, and conversation formatting.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from src.voice_pipeline.system_prompts import (
    count_tokens,
    format_conversation_history,
    get_numerology_system_prompt
)


class TestCountTokens:
    """Test suite for count_tokens function."""

    def test_counts_tokens_with_tiktoken(self):
        """Test that tokens are counted accurately when tiktoken is available."""
        text = "Hello, this is a test message."

        with patch('src.voice_pipeline.system_prompts.tiktoken') as mock_tiktoken:
            mock_encoding = Mock()
            mock_encoding.encode.return_value = [1, 2, 3, 4, 5, 6]  # 6 tokens
            mock_tiktoken.encoding_for_model.return_value = mock_encoding

            result = count_tokens(text)

            assert result == 6
            mock_tiktoken.encoding_for_model.assert_called_once_with("gpt-4")

    def test_estimates_tokens_when_tiktoken_unavailable(self):
        """Test that tokens are estimated when tiktoken is not available."""
        text = "Hello, this is a test message."  # 30 chars

        with patch('src.voice_pipeline.system_prompts.tiktoken', None):
            result = count_tokens(text)

            # Estimation: chars // 4 = 30 // 4 = 7
            assert result == 7

    def test_handles_tiktoken_error_gracefully(self):
        """Test that function falls back to estimation on tiktoken error."""
        text = "Hello, this is a test message."

        with patch('src.voice_pipeline.system_prompts.tiktoken') as mock_tiktoken:
            mock_tiktoken.encoding_for_model.side_effect = Exception("Model not found")

            result = count_tokens(text)

            # Should fall back to estimation
            assert result == len(text) // 4


class TestFormatConversationHistory:
    """Test suite for format_conversation_history function."""

    def test_formats_single_conversation(self):
        """Test formatting of a single conversation."""
        conversations = [
            {
                "date": "2025-11-23T10:30:00Z",
                "topic": "Life Path Number",
                "insights": "User resonates with leadership qualities",
                "numbers": "1, 11"
            }
        ]

        result = format_conversation_history(conversations)

        assert "Previous conversations with this user:" in result
        assert "Nov 23: Life Path Number" in result
        assert "Discussed numbers: 1, 11" in result
        assert "User resonates with leadership" in result

    def test_handles_empty_list(self):
        """Test that empty string is returned for empty conversation list."""
        result = format_conversation_history([])
        assert result == ""

    def test_truncates_long_insights(self):
        """Test that insights longer than 100 chars are truncated."""
        long_insight = "A" * 150  # 150 characters

        conversations = [
            {
                "date": "2025-11-23T10:30:00Z",
                "topic": "Test Topic",
                "insights": long_insight,
                "numbers": ""
            }
        ]

        result = format_conversation_history(conversations)

        # Should truncate to 100 chars
        assert len([line for line in result.split('\n') if long_insight[:100] in line]) > 0
        assert long_insight not in result  # Full insight should not be present

    def test_handles_missing_fields_gracefully(self):
        """Test that function handles missing conversation fields."""
        conversations = [
            {
                "date": "2025-11-23T10:30:00Z",
                "topic": "Test Topic"
                # Missing insights and numbers
            }
        ]

        result = format_conversation_history(conversations)

        assert "Test Topic" in result
        # Should not crash, should handle gracefully


class TestGetNumerologySystemPrompt:
    """Test suite for get_numerology_system_prompt function."""

    def test_generates_prompt_without_conversation_history(self):
        """Test system prompt generation without conversation history."""
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_user.birth_date = datetime(1990, 5, 15)

        with patch('src.voice_pipeline.system_prompts.PROMPT_TEMPLATE_PATH') as mock_path:
            mock_path.read_text.return_value = "Hello {user_name}, born on {birth_date_formatted}"

            result = get_numerology_system_prompt(mock_user)

            assert "Hello Test User" in result
            assert "15/05/1990" in result
            assert "previous conversations" not in result.lower()

    def test_includes_conversation_history_when_provided(self):
        """Test that conversation history is appended to system prompt with enhanced guidance."""
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_user.birth_date = datetime(1990, 5, 15)

        conversation_history = "Previous conversations with this user:\n1. Nov 23: Life Path Number."

        with patch('src.voice_pipeline.system_prompts.PROMPT_TEMPLATE_PATH') as mock_path:
            mock_path.read_text.return_value = "Hello {user_name}"

            result = get_numerology_system_prompt(mock_user, conversation_history=conversation_history)

            assert "Hello Test User" in result
            assert "Previous conversations with this user:" in result
            assert "Life Path Number" in result
            # Check for Vietnamese enhanced conversation history guidance
            assert "Tận dụng lịch sử trò chuyện" in result
            assert "Khi chào hỏi:" in result
            assert "Lần trước chúng ta đã nói về" in result

    def test_handles_none_full_name(self):
        """Test that function handles None full_name gracefully."""
        mock_user = Mock()
        mock_user.full_name = None
        mock_user.birth_date = datetime(1990, 5, 15)

        with patch('src.voice_pipeline.system_prompts.PROMPT_TEMPLATE_PATH') as mock_path:
            mock_path.read_text.return_value = "Hello {user_name}"

            result = get_numerology_system_prompt(mock_user)

            assert "Hello bạn" in result  # Should use Vietnamese "bạn" as fallback

    def test_handles_none_birth_date(self):
        """Test that function handles None birth_date gracefully."""
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_user.birth_date = None

        with patch('src.voice_pipeline.system_prompts.PROMPT_TEMPLATE_PATH') as mock_path:
            mock_path.read_text.return_value = "Born on {birth_date_formatted}"

            result = get_numerology_system_prompt(mock_user)

            assert "Chưa cung cấp" in result  # Vietnamese for "Not provided"

    def test_falls_back_on_file_not_found(self):
        """Test that fallback prompt is used when template file is not found."""
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_user.birth_date = datetime(1990, 5, 15)

        with patch('src.voice_pipeline.system_prompts.PROMPT_TEMPLATE_PATH') as mock_path:
            mock_path.read_text.side_effect = FileNotFoundError()

            result = get_numerology_system_prompt(mock_user)

            # Should return fallback prompt
            assert "Aria" in result  # Fallback contains "Aria"
            assert "Thần Số Học" in result  # Vietnamese content
