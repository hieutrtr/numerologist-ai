"""
Voice Bot Configuration Settings

Centralizes all configuration using Pydantic Settings to avoid magic numbers
and scattered environment variable references.
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables.
    Example: export DATABASE_URL="postgresql://user:pass@host:5432/db"
    """

    # =====================================================================
    # APPLICATION
    # =====================================================================
    app_name: str = "Voice Bot API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # =====================================================================
    # DATABASE (PostgreSQL)
    # =====================================================================
    database_url: str = "postgresql://postgres:password@localhost:5432/voicebot"
    """PostgreSQL connection string. Format: postgresql://user:password@host:port/database"""

    db_echo: bool = False
    """Enable SQL query logging for debugging."""

    db_pool_size: int = 5
    """Number of connections in the pool. Production: 20-50"""

    db_max_overflow: int = 10
    """Maximum overflow connections beyond pool_size."""

    db_pool_pre_ping: bool = True
    """Verify connections before use to prevent stale connections."""

    # =====================================================================
    # JWT AUTHENTICATION
    # =====================================================================
    jwt_secret: str = "dev-secret-change-in-production-MUST-BE-SECURE"
    """
    ⚠️  CRITICAL: MUST be changed in production!
    Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
    """

    algorithm: str = "HS256"
    """JWT signing algorithm."""

    access_token_expire_minutes: int = 30
    """JWT token expiration time in minutes."""

    # =====================================================================
    # VOICE PIPELINE SERVICES
    # =====================================================================
    daily_api_key: str = ""
    """Daily.co API key for WebRTC rooms. Get from: https://dashboard.daily.co/"""

    deepgram_api_key: str = ""
    """Deepgram API key for STT. Get from: https://console.deepgram.com/"""

    azure_openai_api_key: str = ""
    """Azure OpenAI API key. Get from: https://portal.azure.com/"""

    azure_openai_endpoint: str = ""
    """Azure OpenAI endpoint URL. Format: https://your-resource.openai.azure.com/"""

    azure_openai_model_deployment_name: str = "gpt-4"
    """Azure OpenAI deployment name (created in Azure Portal)."""

    azure_openai_api_version: str = "2024-09-01-preview"
    """Azure OpenAI API version."""

    elevenlabs_api_key: str = ""
    """ElevenLabs API key for TTS. Get from: https://elevenlabs.io/"""

    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    """
    ElevenLabs voice ID.
    Options:
    - Rachel (default): 21m00Tcm4TlvDq8ikWAM
    - Charlie: N2lVS1w4EtoT3dr4eOWO
    - Grace: JBFqnCBsd6RMkjW3i8ZA
    """

    # =====================================================================
    # VOICE PIPELINE CONFIGURATION
    # =====================================================================
    voice_language: str = "en"
    """
    Language code for voice conversations.
    Supported: en, vi, es, fr, de, ja, zh, pt
    """

    vad_silence_timeout_ms: int = 1000
    """
    Voice Activity Detection silence timeout in milliseconds.
    Recommended:
    - 500-700ms: Very responsive (may interrupt)
    - 800-1200ms: Balanced
    - 1500-2000ms: Conservative
    """

    # =====================================================================
    # CORS & SECURITY
    # =====================================================================
    cors_origins: list[str] = ["*"]
    """
    Allowed CORS origins.
    Development: ["*"]
    Production: ["https://yourdomain.com"]
    """

    # =====================================================================
    # LOGGING
    # =====================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """Logging level."""

    # =====================================================================
    # FEATURE FLAGS
    # =====================================================================
    enable_docs: bool = True
    """Enable Swagger/ReDoc documentation."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()

__all__ = ["Settings", "settings"]
