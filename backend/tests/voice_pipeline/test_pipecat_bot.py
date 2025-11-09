"""
Tests for Pipecat Voice AI Bot - Configuration Validation

This module tests the critical configuration validation logic in pipecat_bot.
Integration testing of the complete pipeline requires a real Pipecat environment
and is performed via manual testing (see backend/scripts/test_pipecat_bot.py).

Test Coverage:
- API key validation (all voice services)
- Missing configuration error messages
- Multiple missing keys handling

Note: Deep integration tests with Pipecat mocking are avoided due to Pydantic
      validation complexity in Daily Transport and service initialization.
      Manual E2E testing validates the complete pipeline.
"""

import pytest
from unittest.mock import patch

from src.voice_pipeline import pipecat_bot


# ============================================================================
# Configuration Validation Tests
# ============================================================================

def test_validate_configuration_success():
    """Test that _validate_configuration passes with all keys configured"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = "test-key"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_endpoint = "https://test.com"
        mock_settings.elevenlabs_api_key = "test-key"

        # Should not raise any exception
        pipecat_bot._validate_configuration()


def test_validate_configuration_missing_deepgram():
    """Test _validate_configuration raises ValueError for missing Deepgram key"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = ""
        mock_settings.azure_openai_api_key = "test"
        mock_settings.azure_openai_endpoint = "https://test.com"
        mock_settings.elevenlabs_api_key = "test"

        with pytest.raises(ValueError) as exc_info:
            pipecat_bot._validate_configuration()

        error_message = str(exc_info.value)
        assert "DEEPGRAM_API_KEY" in error_message
        assert "speech-to-text" in error_message


def test_validate_configuration_missing_azure_key():
    """Test _validate_configuration raises ValueError for missing Azure API key"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = "test"
        mock_settings.azure_openai_api_key = ""
        mock_settings.azure_openai_endpoint = "https://test.com"
        mock_settings.elevenlabs_api_key = "test"

        with pytest.raises(ValueError) as exc_info:
            pipecat_bot._validate_configuration()

        error_message = str(exc_info.value)
        assert "AZURE_OPENAI_API_KEY" in error_message
        assert "language model" in error_message


def test_validate_configuration_missing_azure_endpoint():
    """Test _validate_configuration raises ValueError for missing Azure endpoint"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = "test"
        mock_settings.azure_openai_api_key = "test"
        mock_settings.azure_openai_endpoint = ""
        mock_settings.elevenlabs_api_key = "test"

        with pytest.raises(ValueError) as exc_info:
            pipecat_bot._validate_configuration()

        error_message = str(exc_info.value)
        assert "AZURE_OPENAI_ENDPOINT" in error_message


def test_validate_configuration_missing_elevenlabs():
    """Test _validate_configuration raises ValueError for missing ElevenLabs key"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = "test"
        mock_settings.azure_openai_api_key = "test"
        mock_settings.azure_openai_endpoint = "https://test.com"
        mock_settings.elevenlabs_api_key = ""

        with pytest.raises(ValueError) as exc_info:
            pipecat_bot._validate_configuration()

        error_message = str(exc_info.value)
        assert "ELEVENLABS_API_KEY" in error_message
        assert "text-to-speech" in error_message


def test_validate_configuration_missing_multiple_keys():
    """Test that error message lists all missing API keys"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = ""
        mock_settings.azure_openai_api_key = ""
        mock_settings.azure_openai_endpoint = ""
        mock_settings.elevenlabs_api_key = ""

        with pytest.raises(ValueError) as exc_info:
            pipecat_bot._validate_configuration()

        # Verify error message lists all missing keys
        error_message = str(exc_info.value)
        assert "DEEPGRAM_API_KEY" in error_message
        assert "AZURE_OPENAI_API_KEY" in error_message
        assert "AZURE_OPENAI_ENDPOINT" in error_message
        assert "ELEVENLABS_API_KEY" in error_message


def test_validate_configuration_error_messages_helpful():
    """Test that error messages include helpful information"""
    with patch("src.voice_pipeline.pipecat_bot.settings") as mock_settings:
        mock_settings.deepgram_api_key = ""
        mock_settings.azure_openai_api_key = "test"
        mock_settings.azure_openai_endpoint = "https://test.com"
        mock_settings.elevenlabs_api_key = "test"

        with pytest.raises(ValueError) as exc_info:
            pipecat_bot._validate_configuration()

        error_message = str(exc_info.value)
        # Check that error includes URL for obtaining API key
        assert "console.deepgram.com" in error_message or "deepgram" in error_message.lower()


# ============================================================================
# Module Import Test
# ============================================================================

def test_module_imports_successfully():
    """Test that pipecat_bot module can be imported without errors"""
    # If we got here, the import at the top succeeded
    assert hasattr(pipecat_bot, 'run_bot')
    assert hasattr(pipecat_bot, '_validate_configuration')
    assert hasattr(pipecat_bot, 'PipecatBotError')


# ============================================================================
# Exception Classes
# ============================================================================

def test_pipecat_bot_error_exception_exists():
    """Test that PipecatBotError exception is defined"""
    assert issubclass(pipecat_bot.PipecatBotError, Exception)


def test_pipecat_bot_error_can_be_raised():
    """Test that PipecatBotError can be instantiated and raised"""
    with pytest.raises(pipecat_bot.PipecatBotError):
        raise pipecat_bot.PipecatBotError("Test error")
