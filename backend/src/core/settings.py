"""
Application settings and configuration management.

Centralizes all configuration using Pydantic Settings to avoid magic numbers,
hardcoding, and scattered environment variable references.

Configuration is loaded from environment variables with sensible defaults for
local development. Override via environment variables in production.

Usage:
    from src.core.settings import settings

    db_url = settings.database_url
    redis_url = settings.redis_url
    pool_size = settings.db_pool_size
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables. For example:
    - export DATABASE_URL="postgresql://user:pass@host:5432/db"
    - export REDIS_URL="redis://localhost:6379"
    - export DEBUG=true
    """

    # =====================================================================
    # APPLICATION
    # =====================================================================
    app_name: str = "Numerologist AI API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # =====================================================================
    # DATABASE (PostgreSQL)
    # =====================================================================
    database_url: str = (
        "postgresql://postgres:password@localhost:5432/numerologist"
    )
    """
    PostgreSQL connection string.

    Format: postgresql://user:password@host:port/database
    Environment variable: DATABASE_URL
    """

    db_echo: bool = False
    """Enable SQL query logging. Set to True for debugging."""

    db_pool_size: int = 5
    """
    Number of connections to maintain in the pool.

    Recommended values:
    - Development: 5
    - Staging: 10
    - Production: 20-50 (depending on concurrency)
    """

    db_max_overflow: int = 10
    """
    Maximum overflow connections beyond pool_size.

    When pool is full, additional connections up to this limit are created.
    Recommended: 2-3x pool_size
    """

    db_pool_pre_ping: bool = True
    """
    Verify connections before using them.

    Detects connections that have been closed or invalidated.
    Prevents "connection reset by peer" errors.
    """

    db_echo_pool: bool = False
    """Enable connection pool logging. Useful for debugging connection issues."""

    # =====================================================================
    # REDIS (Cache & Session Store)
    # =====================================================================
    redis_url: str = "redis://localhost:6379"
    """
    Redis connection string.

    Format: redis://[:password]@host:port/db
    Environment variable: REDIS_URL

    Examples:
    - Local: redis://localhost:6379
    - With password: redis://:password@host:6379
    - With database: redis://localhost:6379/1
    """

    redis_pool_size: int = 10
    """
    Maximum number of connections in Redis connection pool.

    Recommended values:
    - Development: 5-10
    - Production: 20-50
    """

    redis_pool_timeout: int = 30
    """Timeout in seconds for acquiring a connection from Redis pool."""

    redis_socket_keepalive: bool = True
    """Enable TCP keepalive for Redis connections."""

    redis_socket_keepalive_options: dict = {
        "TCP_KEEPIDLE": 60,
        "TCP_KEEPINTVL": 10,
        "TCP_KEEPCNT": 5,
    }
    """TCP keepalive socket options for Redis connections."""

    # =====================================================================
    # JWT AUTHENTICATION
    # =====================================================================
    jwt_secret: str = "dev-secret-change-in-production-MUST-BE-SECURE"
    """
    Secret key for JWT token signing and verification.

    ⚠️  CRITICAL: MUST be changed in production via environment variable!

    Requirements:
    - Minimum 32 characters
    - Use cryptographically random string
    - Never commit production secret to version control
    - Rotate periodically for security

    Environment variable: JWT_SECRET or SECRET_KEY

    Generate secure secret:
        python -c "import secrets; print(secrets.token_urlsafe(32))"
    """

    secret_key: str = ""
    """Alias for jwt_secret (legacy support for older .env files)."""

    algorithm: str = "HS256"
    """JWT algorithm for token signing. Standard: HS256."""

    access_token_expire_minutes: int = 30
    """JWT access token expiration time in minutes."""

    # =====================================================================
    # GOOGLE OAUTH
    # =====================================================================
    google_web_client_id: str = ""
    """
    Google OAuth 2.0 Web Client ID for backend token verification.

    Used to verify Google ID tokens returned by frontend.
    Get from: https://console.cloud.google.com/
    - Create OAuth 2.0 credentials (Web application type)
    - Copy the Client ID

    Environment variable: GOOGLE_WEB_CLIENT_ID
    """

    google_client_id: str = ""
    """Alias for google_web_client_id (legacy support for older .env files)."""

    google_android_client_id: str = ""
    """
    Google OAuth 2.0 Android Client ID for frontend integration.

    Used in mobile app for Google Sign-In SDK configuration.
    Get from: https://console.cloud.google.com/
    - Add Android as an Authorized JavaScript Origins
    - Copy the Client ID

    Environment variable: GOOGLE_ANDROID_CLIENT_ID
    """

    # =====================================================================
    # CORS & SECURITY
    # =====================================================================
    cors_origins: list[str] = ["*"]
    """
    Allowed CORS origins.

    Development: ["*"] allows all
    Production: Should be specific domains only
    """

    cors_allow_credentials: bool = True
    """Allow cookies/credentials in CORS requests."""

    cors_allow_methods: list[str] = ["*"]
    """Allowed HTTP methods for CORS."""

    cors_allow_headers: list[str] = ["*"]
    """Allowed headers for CORS."""

    # =====================================================================
    # API ENDPOINTS
    # =====================================================================
    api_prefix: str = "/api"
    """Prefix for API routes. Example: /api/v1"""

    health_check_endpoint: str = "/health"
    """Health check endpoint path."""

    # =====================================================================
    # LOGGING & MONITORING
    # =====================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """Logging level."""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    """Logging format string."""

    # =====================================================================
    # TIMEOUTS & LIMITS
    # =====================================================================
    request_timeout: int = 30
    """Request timeout in seconds."""

    max_connection_attempts: int = 3
    """Maximum database connection retry attempts."""

    connection_retry_delay: float = 1.0
    """Delay in seconds between connection retry attempts."""

    # =====================================================================
    # FEATURE FLAGS
    # =====================================================================
    enable_docs: bool = True
    """Enable Swagger documentation (/docs endpoint)."""

    enable_redoc: bool = True
    """Enable ReDoc documentation (/redoc endpoint)."""

    # =====================================================================
    # VOICE PIPELINE LANGUAGE CONFIGURATION
    # =====================================================================
    voice_language: str = "en"
    """
    Language code for voice conversation pipeline.

    Supported languages:
    - "en": English
    - "vi": Vietnamese
    - "es": Spanish
    - "fr": French
    - "de": German
    - "ja": Japanese
    - "zh": Chinese
    - "pt": Portuguese
    - See Azure Speech docs for full list: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support

    Environment variable: VOICE_LANGUAGE
    Default: "en" (English)
    """

    # =====================================================================
    # VOICE PIPELINE VAD (Voice Activity Detection) CONFIGURATION
    # =====================================================================
    vad_silence_timeout_ms: int = 1000
    """
    Silence timeout in milliseconds for ending user speech.

    When the VAD detects silence longer than this duration, it signals the end of user speech.
    Lower values = faster response but more false positives (bot interrupts)
    Higher values = more natural but slower response

    Recommended values:
    - 500-700ms: Very responsive (aggressive)
    - 800-1200ms: Balanced (recommended for conversations)
    - 1500-2000ms: Conservative (waits longer for pauses within speech)

    Environment variable: VAD_SILENCE_TIMEOUT_MS
    Default: 1000ms
    """

    # =====================================================================
    # VOICE PIPELINE SERVICES (Epic 3)
    # =====================================================================
    daily_api_key: str = ""
    """
    Daily.co API key for WebRTC room management.

    Get from: https://dashboard.daily.co/ → Developers → API Keys
    Environment variable: DAILY_API_KEY
    Required for voice conversation infrastructure.
    """

    deepgram_api_key: str = ""
    """
    [DEPRECATED] Deepgram API key - No longer used.

    The voice pipeline now uses Azure Speech Services for STT.
    This setting is kept for backward compatibility but is not required.
    Environment variable: DEEPGRAM_API_KEY
    """

    azure_openai_api_key: str = ""
    """
    Azure OpenAI API key for language model (GPT-5-mini).

    Get from: https://portal.azure.com/ → Azure OpenAI Service → Keys and Endpoint
    Environment variable: AZURE_OPENAI_API_KEY
    """

    azure_openai_endpoint: str = ""
    """
    Azure OpenAI endpoint URL.

    Format: https://your-resource.openai.azure.com/
    Environment variable: AZURE_OPENAI_ENDPOINT
    """

    azure_openai_model_deployment_name: str = "gpt-5-mini-deployment"
    """
    Azure OpenAI deployment name (created in Azure).

    Environment variable: AZURE_OPENAI_MODEL_DEPLOYMENT_NAME
    """

    azure_openai_model_name: str = "gpt-5-mini"
    """
    Azure OpenAI model name specification.

    Environment variable: AZURE_OPENAI_MODEL_NAME
    """
    azure_openai_api_version: str = "2024-09-01-preview"
    """
    Azure OpenAI API version.
    Environment variable: AZURE_OPENAI_API_VERSION
    """

    # -------------------------------------------------------------------------
    # Azure Speech Service (STT) - Separate from Azure OpenAI
    # -------------------------------------------------------------------------

    azure_speech_api_key: str = ""
    """
    Azure Speech Services API key for speech-to-text.

    Get from: https://portal.azure.com/ → Speech Services → Keys and Endpoint
    Environment variable: AZURE_SPEECH_API_KEY
    """

    azure_speech_region: str = "eastus"
    """
    Azure Speech Services region.

    Common regions: eastus, westus, westeurope, southeastasia
    Environment variable: AZURE_SPEECH_REGION
    """

    elevenlabs_api_key: str = ""
    """
    ElevenLabs API key for text-to-speech synthesis.

    Get from: https://elevenlabs.io/ → Profile → API Keys
    Environment variable: ELEVENLABS_API_KEY
    """

    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    """
    ElevenLabs voice ID (default: Rachel).

    Other options: Charlie (N2lVS1w4EtoT3dr4eOWO), Grace (JBFqnCBsd6RMkjW3i8ZA)
    Environment variable: ELEVENLABS_VOICE_ID
    """

    elevenlabs_model: str = "eleven_turbo_v2_5"
    """
    ElevenLabs TTS model for voice synthesis.

    Available models:
    - eleven_turbo_v2_5: 32 languages, 300ms latency, supports Vietnamese (recommended for multilingual)
    - eleven_flash_v2_5: Newest model, recommended replacement for turbo (default by Pipecat)
    - eleven_turbo_v2: English only, ultra-low latency (<75ms)
    - eleven_multilingual_v2: 29 languages, highest quality but slower

    Environment variable: ELEVENLABS_MODEL
    """

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()

__all__ = ["Settings", "settings"]
