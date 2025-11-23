"""
Pipecat Voice AI Bot Implementation

This module implements a voice-enabled AI bot using the Pipecat framework, integrating:
- Daily.co WebRTC transport for real-time audio communication
- Deepgram for speech-to-text transcription
- Azure OpenAI GPT-5-mini for language understanding and response generation
- ElevenLabs for natural voice synthesis

The bot creates an end-to-end voice conversation pipeline that processes user speech,
generates AI responses, and speaks them back naturally with minimal latency.

Architecture:
    User Audio (mic) → Daily.co WebRTC → Deepgram STT → Azure OpenAI LLM
    → ElevenLabs TTS → Daily.co WebRTC → User Audio (speakers)

Usage:
    from src.voice_pipeline import pipecat_bot
    from src.services import daily_service

    # Create Daily.co room
    room_info = await daily_service.create_room("conversation-123")

    # Spawn bot in background
    import asyncio
    task = asyncio.create_task(
        pipecat_bot.run_bot(room_info["room_url"], room_info["meeting_token"])
    )

Configuration:
    Requires environment variables (loaded via settings.py):
    - DEEPGRAM_API_KEY: Speech-to-text service
    - AZURE_OPENAI_API_KEY: Language model service
    - AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
    - ELEVENLABS_API_KEY: Text-to-speech service
    - ELEVENLABS_MODEL: TTS model (default: eleven_turbo_v2_5 for multilingual support)

References:
    - Pipecat Documentation: https://docs.pipecat.ai/
    - Daily.co Python SDK: https://docs.daily.co/reference/daily-python
    - Deepgram API: https://developers.deepgram.com/
    - Azure OpenAI: https://learn.microsoft.com/en-us/azure/ai-services/openai/
    - ElevenLabs API: https://docs.elevenlabs.io/
"""

import logging
import asyncio
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

# Pipecat core components
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.pipeline.runner import PipelineRunner

# Daily.co WebRTC transport
from pipecat.transports.daily.transport import DailyTransport, DailyParams

# Voice Activity Detection
from pipecat.audio.vad.silero import SileroVADAnalyzer

# Speech services
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.azure.llm import AzureLLMService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from deepgram import LiveOptions
from pipecat.transcriptions.language import Language

# Message aggregators for conversation history
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

# Application settings and models
from src.core.settings import settings
from src.models.user import User
from src.models.conversation_message import ConversationMessage, MessageRole
from src.core.database import engine
from sqlmodel import Session

# Configure logger
logger = logging.getLogger(__name__)


class PipecatBotError(Exception):
    """
    Base exception for Pipecat bot errors.

    This exception wraps errors that occur during bot initialization,
    service configuration, or pipeline execution.
    """
    pass


async def _save_message_async(
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    metadata: Optional[dict] = None
) -> None:
    """
    Save a conversation message to the database asynchronously (non-blocking).

    This function runs database operations in a thread pool to avoid blocking
    the voice pipeline. Errors are logged but don't propagate to prevent
    breaking the conversation flow.

    Args:
        conversation_id: UUID of the conversation this message belongs to
        role: Message sender role (user or assistant)
        content: Full text content of the message
        metadata: Optional dict with additional data (function calls, etc.)

    Notes:
        - Uses asyncio.to_thread for non-blocking execution
        - Errors are logged but swallowed to maintain voice pipeline stability
        - Creates new database session for each save (thread-safe)
    """
    def _db_save():
        """Inner function that performs the actual database save."""
        try:
            with Session(engine) as session:
                message = ConversationMessage(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    timestamp=datetime.now(timezone.utc),
                    message_metadata=metadata or {}
                )
                session.add(message)
                session.commit()
                logger.debug(
                    f"Saved {role.value} message to conversation {conversation_id}: "
                    f"{content[:50]}..." if len(content) > 50 else content
                )
        except Exception as e:
            # Log error but don't propagate - voice pipeline must continue
            logger.error(
                f"Failed to save {role.value} message to database: {e}",
                exc_info=True,
                extra={
                    "conversation_id": str(conversation_id),
                    "role": role.value,
                    "content_length": len(content)
                }
            )

    # Run database save in thread pool (non-blocking)
    try:
        await asyncio.to_thread(_db_save)
    except Exception as e:
        # This should rarely happen (thread pool errors)
        logger.error(f"Thread pool error saving message: {e}", exc_info=True)


async def run_bot(
    room_url: str,
    token: str,
    conversation_id: Optional[UUID] = None,
    user: Optional[User] = None
) -> Optional[PipelineTask]:
    """
    Run a Pipecat voice AI bot in a Daily.co room with conversation message saving.

    This function creates and executes a complete voice conversation pipeline:
    1. Connects to Daily.co room via DailyTransport
    2. Initializes speech services (Deepgram STT, Azure OpenAI LLM, ElevenLabs TTS)
    3. Builds Pipecat pipeline with proper component ordering
    4. Initializes system prompt based on user context and language
    5. Saves all messages (user and assistant) to database asynchronously
    6. Runs pipeline asynchronously until room closes or bot is stopped

    The bot responds to user speech with a numerology-expert system prompt generated
    from the User object. For Vietnamese language (vi), uses specialized system prompt
    from system_prompts.get_numerology_system_prompt(user). For other languages,
    falls back to default generic greeting.

    Args:
        room_url: Full URL to the Daily.co room (e.g., "https://domain.daily.co/room-name")
        token: JWT meeting token for secure room access
        conversation_id: Optional UUID of the conversation for message saving.
                        If provided, all messages will be saved to database.
        user: Optional User object for personalization. If provided and language is Vietnamese,
              generates personalized numerology system prompt. If None, uses generic greeting.

    Returns:
        PipelineTask instance for lifecycle management (stop, monitor status)
        Returns None if initialization fails

    Raises:
        ValueError: If required API keys are not configured
        PipecatBotError: If bot initialization or service setup fails

    Example:
        >>> from src.models.user import User
        >>> from uuid import UUID
        >>> room_info = await daily_service.create_room("conv-123")
        >>> conv_id = UUID("...")  # Conversation ID from database
        >>> user = User(id=..., full_name="Nguyễn Văn A", birth_date=date(1990, 5, 15), ...)
        >>> task = await run_bot(
        ...     room_info["room_url"],
        ...     room_info["meeting_token"],
        ...     conversation_id=conv_id,
        ...     user=user
        ... )
        >>> # Bot now running in background, handles voice interactions and saves messages
        >>> # To stop: await task.cancel()

    Notes:
        - Bot runs until Daily.co room closes or pipeline is explicitly stopped
        - System prompt personalized when user object provided for Vietnamese conversations
        - All errors are logged with descriptive messages
        - Pipeline uses lazy validation pattern (validates at runtime, not import)
        - VAD (Voice Activity Detection) enabled for natural conversation flow
        - Message saving is non-blocking and won't affect voice latency (<3s requirement)
        - If message save fails, error is logged but conversation continues normally
    """
    try:
        # Validate configuration (lazy validation pattern)
        logger.info(f"Starting Pipecat bot for room: {room_url}")
        _validate_configuration()

        # Configure Daily.co transport with VAD
        logger.info("Configuring Daily.co transport with VAD")
        transport = DailyTransport(
            room_url,
            token,
            "Numerology AI Bot",
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            )
        )

        # Initialize speech services
        logger.info(f"Initializing speech services (language: {settings.voice_language})")

        # Deepgram: Speech-to-Text with language configuration
        logger.info(f"Configuring Deepgram for language: {settings.voice_language}")

        # Map language code to Language enum
        language_map = {
            "en": Language.EN,
            "vi": Language.VI,
            "es": Language.ES,
            "fr": Language.FR,
            "de": Language.DE,
            "ja": Language.JA,
            "zh": Language.ZH,
            "pt": Language.PT,
        }
        language_enum = language_map.get(settings.voice_language, Language.EN)

        stt = DeepgramSTTService(
            api_key=settings.deepgram_api_key,
            live_options=LiveOptions(
                language=language_enum,
                model="nova-3-general",
                vad_events=True,  # Enable VAD event detection for silence detection
                endpointing=True,  # Automatic endpoint detection (stops recording when speech ends)
                interim_results=True,  # Show real-time transcription
                punctuate=True,  # Add punctuation
                smart_format=True,  # Format numbers, URLs, etc.
            ),
        )

        # Azure OpenAI: Language Model
        llm = AzureLLMService(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            model=settings.azure_openai_model_deployment_name,
            api_version=settings.azure_openai_api_version,
            run_in_parallel=False,  # Enable sequential function calling
        )

        # Import numerology function handlers
        from src.voice_pipeline.function_handlers import (
            handle_calculate_life_path,
            handle_calculate_expression,
            handle_calculate_soul_urge,
            handle_get_interpretation
        )

        # Register function handlers with LLM service
        llm.register_function("calculate_life_path", handle_calculate_life_path, cancel_on_interruption=False)
        llm.register_function("calculate_expression_number", handle_calculate_expression, cancel_on_interruption=False)
        llm.register_function("calculate_soul_urge_number", handle_calculate_soul_urge, cancel_on_interruption=False)
        llm.register_function("get_numerology_interpretation", handle_get_interpretation, cancel_on_interruption=False)

        logger.info("Registered 4 numerology function handlers with LLM service")

        # ElevenLabs: Text-to-Speech with model configuration
        logger.info(f"Configuring ElevenLabs TTS with model: {settings.elevenlabs_model}")
        tts = ElevenLabsTTSService(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
            model=settings.elevenlabs_model,
        )

        # Initialize conversation with language-aware system prompt
        # For Vietnamese with user object: use specialized numerology prompt
        # Otherwise: use generic language-specific greeting
        if settings.voice_language == "vi" and user is not None:
            # Vietnamese with user context: use specialized numerology system prompt
            from src.voice_pipeline.system_prompts import get_numerology_system_prompt
            system_prompt = get_numerology_system_prompt(user)
            logger.info(f"Generated Vietnamese numerology system prompt for user: {user.full_name}")
        else:
            # Generic language-specific greetings (for non-Vietnamese or no user context)
            generic_prompts = {
                "en": "You are a friendly AI assistant. Greet the user warmly and ask how you can help them today.",
                "vi": "Bạn là một trợ lý AI thân thiện. Chào người dùng một cách ấm áp và hỏi bạn có thể giúp gì cho họ hôm nay.",
                "es": "Eres un asistente de IA amable. Saluda al usuario calurosamente y pregunta cómo puedes ayudarlo hoy.",
                "fr": "Vous êtes un assistant IA amical. Accueillez chaleureusement l'utilisateur et demandez comment vous pouvez l'aider aujourd'hui.",
                "de": "Du bist ein freundlicher KI-Assistent. Grüße den Benutzer warm und frage, wie du ihm heute helfen kannst.",
                "ja": "あなたはフレンドリーなAIアシスタントです。ユーザーに温かく挨拶し、今日どのように手伝えるか尋ねます。",
                "zh": "您是一个友好的AI助手。热情地问候用户，并询问您今天如何能帮助他们。",
                "pt": "Você é um assistente de IA amigável. Cumprimente o usuário calurosamente e pergunte como você pode ajudá-lo hoje.",
            }

            system_prompt = generic_prompts.get(
                settings.voice_language,
                generic_prompts["en"]  # Fallback to English
            )

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Import numerology function calling tools
        from src.voice_pipeline.numerology_functions import numerology_tools

        # Create LLM context for managing conversation history with tools
        llm_context = OpenAILLMContext(messages=messages, tools=numerology_tools)
        logger.info(f"Registered numerology tools with LLM context")

        # Hook message saving if conversation_id provided
        if conversation_id:
            logger.info(f"Enabling message saving for conversation {conversation_id}")

            # Wrap context to intercept messages
            original_add_message = llm_context.add_message

            def add_message_with_save(message: dict):
                """Intercept add_message calls to save messages to database."""
                # Call original method
                result = original_add_message(message)

                # Save message asynchronously (fire-and-forget)
                role_str = message.get("role", "")
                content = message.get("content", "")

                if role_str == "user" and content:
                    # Save user message
                    asyncio.create_task(
                        _save_message_async(
                            conversation_id,
                            MessageRole.USER,
                            content
                        )
                    )
                elif role_str == "assistant" and content:
                    # Save assistant message
                    asyncio.create_task(
                        _save_message_async(
                            conversation_id,
                            MessageRole.ASSISTANT,
                            content
                        )
                    )

                return result

            # Replace add_message method with wrapped version
            llm_context.add_message = add_message_with_save
            logger.info("Message saving hooks installed")

        # Create context aggregator using the LLM service
        # This ensures proper function call result handling
        context_aggregator = llm.create_context_aggregator(llm_context)

        # Build complete pipeline
        # Order is critical: input → stt → user_agg → llm → tts → output → assistant_agg
        logger.info("Building voice pipeline")
        pipeline = Pipeline([
            transport.input(),              # 1. Audio from user (WebRTC)
            stt,                            # 2. Speech-to-text (Deepgram)
            context_aggregator.user(),      # 3. Collect user message (using context aggregator)
            llm,                            # 4. Generate response (Azure OpenAI)
            tts,                            # 5. Text-to-speech (ElevenLabs)
            transport.output(),             # 6. Audio to user (WebRTC)
            context_aggregator.assistant(), # 7. Store assistant message (using context aggregator)
        ])

        # Create and run pipeline task
        logger.info("Starting pipeline runner")
        task = PipelineTask(pipeline, params=PipelineParams())

        # Run pipeline using PipelineRunner (this is a blocking async call that runs until stopped)
        runner = PipelineRunner()
        await runner.run(task)

        logger.info("Pipeline execution completed")
        return task

    except ValueError as e:
        # Configuration errors (missing API keys)
        logger.error(f"Configuration error: {e}", exc_info=True)
        raise

    except Exception as e:
        # Other errors (service initialization, connection failures)
        error_msg = f"Failed to start Pipecat bot: {type(e).__name__}: {e}"
        logger.error(error_msg, exc_info=True)
        raise PipecatBotError(error_msg) from e


def _validate_configuration() -> None:
    """
    Validate that all required API keys are configured.

    This implements the lazy validation pattern: settings are loaded at import time,
    but validation occurs at function call time. This allows tests to mock settings
    without triggering import-time failures.

    Raises:
        ValueError: If any required API key is missing, with descriptive message
                   indicating which key needs to be configured

    Notes:
        - Checks three external service API keys: Deepgram, Azure OpenAI, ElevenLabs
        - Validates Azure OpenAI endpoint URL separately
        - Error messages include instructions for obtaining API keys
    """
    missing_keys = []

    if not settings.deepgram_api_key:
        missing_keys.append(
            "DEEPGRAM_API_KEY (speech-to-text)\n"
            "  Get from: https://console.deepgram.com/ → API Keys"
        )

    if not settings.azure_openai_api_key:
        missing_keys.append(
            "AZURE_OPENAI_API_KEY (language model)\n"
            "  Get from: https://portal.azure.com/ → Azure OpenAI Service → Keys"
        )

    if not settings.azure_openai_endpoint:
        missing_keys.append(
            "AZURE_OPENAI_ENDPOINT (Azure endpoint URL)\n"
            "  Get from: https://portal.azure.com/ → Azure OpenAI Service → Endpoint"
        )

    if not settings.elevenlabs_api_key:
        missing_keys.append(
            "ELEVENLABS_API_KEY (text-to-speech)\n"
            "  Get from: https://elevenlabs.io/ → Profile → API Keys"
        )

    if missing_keys:
        error_message = (
            "Voice pipeline API keys not configured. "
            "Set the following environment variables in .env file:\n\n" +
            "\n\n".join(missing_keys) +
            "\n\nSee backend/.env.example for setup instructions."
        )
        raise ValueError(error_message)

    logger.debug("All API keys validated successfully")


# Manual testing support
"""
Manual Testing Instructions:

1. Ensure all API keys are configured in backend/.env:
   - DEEPGRAM_API_KEY
   - AZURE_OPENAI_API_KEY
   - AZURE_OPENAI_ENDPOINT
   - ELEVENLABS_API_KEY

2. Create a test script (backend/scripts/test_pipecat_bot.py):

   import asyncio
   from src.services import daily_service
   from src.voice_pipeline import pipecat_bot

   async def main():
       # Create Daily.co room
       room = await daily_service.create_room("manual-test-001")
       print(f"Room URL: {room['room_url']}")
       print("Join this URL in your browser to test voice interaction")

       # Run bot
       await pipecat_bot.run_bot(room['room_url'], room['meeting_token'])

   if __name__ == "__main__":
       asyncio.run(main())

3. Run test script: python backend/scripts/test_pipecat_bot.py

4. Open the room URL in Chrome/Firefox (enable microphone)

5. Speak: "Hello"

6. Bot should respond with greeting

Expected behavior:
- Bot joins room automatically
- User speech transcribed in real-time
- AI generates contextual response
- Response spoken naturally via ElevenLabs voice
- Latency target: <1 second end-to-end
"""
