"""
Pipecat Voice AI Bot Implementation - BOILERPLATE TEMPLATE

This is a production-ready template for building voice AI bots with Pipecat.
Customize the system prompt and function calling to fit your use case.

Key Features:
- Daily.co WebRTC transport
- Deepgram STT (multi-language)
- Azure OpenAI LLM
- ElevenLabs TTS
- Function calling support
- Proper context aggregation (prevents infinite loops)

Usage:
    from voice_pipeline import pipecat_bot

    room_info = await daily_service.create_room("conversation-123")
    task = await pipecat_bot.run_bot(room_info["room_url"], room_info["meeting_token"])
"""

import logging
from typing import Optional

# Pipecat core
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

# Context management
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

# Application settings
from core.settings import settings

# Import your function definitions and handlers
from voice_pipeline.function_schemas import function_tools
from voice_pipeline.function_handlers import (
    # TODO: Import your function handlers here
    # handle_your_function,
)

# Configure logger
logger = logging.getLogger(__name__)


class PipecatBotError(Exception):
    """Base exception for Pipecat bot errors."""
    pass


async def run_bot(
    room_url: str,
    token: str,
    user_data: Optional[dict] = None
) -> Optional[PipelineTask]:
    """
    Run a Pipecat voice AI bot in a Daily.co room.

    This creates a complete voice conversation pipeline:
    1. WebRTC transport (Daily.co)
    2. Speech-to-text (Deepgram)
    3. Language model (Azure OpenAI) with function calling
    4. Text-to-speech (ElevenLabs)
    5. Context aggregation (proper history management)

    Args:
        room_url: Daily.co room URL
        token: JWT meeting token
        user_data: Optional user context for personalization

    Returns:
        PipelineTask for lifecycle management

    Raises:
        ValueError: If required API keys are missing
        PipecatBotError: If initialization fails

    Example:
        >>> room = await daily_service.create_room("conv-123")
        >>> task = await run_bot(room["room_url"], room["meeting_token"])
    """
    try:
        logger.info(f"Starting voice bot for room: {room_url}")
        _validate_configuration()

        # =====================================================================
        # 1. CONFIGURE TRANSPORT (Daily.co WebRTC)
        # =====================================================================
        logger.info("Configuring Daily.co transport with VAD")
        transport = DailyTransport(
            room_url,
            token,
            "Voice AI Bot",
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            )
        )

        # =====================================================================
        # 2. INITIALIZE SPEECH SERVICES
        # =====================================================================
        logger.info(f"Initializing speech services (language: {settings.voice_language})")

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

        # Deepgram: Speech-to-Text
        stt = DeepgramSTTService(
            api_key=settings.deepgram_api_key,
            live_options=LiveOptions(
                language=language_enum,
                model="nova-3-general",
                vad_events=True,
                endpointing=True,
                interim_results=True,
                punctuate=True,
                smart_format=True,
            ),
        )

        # Azure OpenAI: Language Model
        llm = AzureLLMService(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            model=settings.azure_openai_model_deployment_name,
            api_version=settings.azure_openai_api_version,
            run_in_parallel=False,  # Sequential function calling
        )

        # =====================================================================
        # 3. REGISTER FUNCTION HANDLERS
        # =====================================================================
        # TODO: Register your function handlers here
        # llm.register_function("your_function_name", handle_your_function,
        #                      cancel_on_interruption=False)

        logger.info("Function handlers registered")

        # ElevenLabs: Text-to-Speech
        tts = ElevenLabsTTSService(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
        )

        # =====================================================================
        # 4. CONFIGURE SYSTEM PROMPT & CONTEXT
        # =====================================================================
        # TODO: Customize this system prompt for your use case
        system_prompt = _get_system_prompt(user_data)

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        # Create LLM context with function calling tools
        llm_context = OpenAILLMContext(
            messages=messages,
            tools=function_tools  # Your function definitions
        )

        logger.info("LLM context created with function tools")

        # =====================================================================
        # 5. CREATE CONTEXT AGGREGATOR (CRITICAL!)
        # =====================================================================
        # IMPORTANT: Use llm.create_context_aggregator() to ensure proper
        # function call result handling. This prevents infinite loops.
        context_aggregator = llm.create_context_aggregator(llm_context)

        # =====================================================================
        # 6. BUILD PIPELINE
        # =====================================================================
        logger.info("Building voice pipeline")
        pipeline = Pipeline([
            transport.input(),              # 1. Audio from user
            stt,                           # 2. Speech-to-text
            context_aggregator.user(),     # 3. Collect user message
            llm,                          # 4. Generate response (with function calls)
            tts,                          # 5. Text-to-speech
            transport.output(),           # 6. Audio to user
            context_aggregator.assistant(), # 7. Store assistant response + function results
        ])

        # =====================================================================
        # 7. RUN PIPELINE
        # =====================================================================
        logger.info("Starting pipeline runner")
        task = PipelineTask(pipeline, params=PipelineParams())

        runner = PipelineRunner()
        await runner.run(task)

        logger.info("Pipeline execution completed")
        return task

    except ValueError as e:
        logger.error(f"Configuration error: {e}", exc_info=True)
        raise

    except Exception as e:
        error_msg = f"Failed to start voice bot: {type(e).__name__}: {e}"
        logger.error(error_msg, exc_info=True)
        raise PipecatBotError(error_msg) from e


def _validate_configuration() -> None:
    """
    Validate that all required API keys are configured.

    Raises:
        ValueError: If any required key is missing
    """
    missing_keys = []

    if not settings.deepgram_api_key:
        missing_keys.append("DEEPGRAM_API_KEY (speech-to-text)")

    if not settings.azure_openai_api_key:
        missing_keys.append("AZURE_OPENAI_API_KEY (language model)")

    if not settings.azure_openai_endpoint:
        missing_keys.append("AZURE_OPENAI_ENDPOINT")

    if not settings.elevenlabs_api_key:
        missing_keys.append("ELEVENLABS_API_KEY (text-to-speech)")

    if missing_keys:
        error_message = (
            "Voice pipeline API keys not configured. "
            "Set the following environment variables in .env file:\\n\\n" +
            "\\n".join(f"  - {key}" for key in missing_keys) +
            "\\n\\nSee .env.example for setup instructions."
        )
        raise ValueError(error_message)

    logger.debug("All API keys validated successfully")


def _get_system_prompt(user_data: Optional[dict] = None) -> str:
    """
    Get system prompt for the AI assistant.

    TODO: Customize this for your specific use case!

    Args:
        user_data: Optional user context for personalization

    Returns:
        System prompt string
    """
    # TODO: Customize your system prompt here
    base_prompt = """
    You are a helpful AI voice assistant.

    AVAILABLE TOOLS:
    - List your functions here with descriptions

    GUIDELINES:
    - Be friendly and conversational
    - Use tools when appropriate
    - Explain results clearly
    - Keep responses concise for voice
    """

    # Add personalization if user data provided
    if user_data:
        user_name = user_data.get("name", "there")
        base_prompt += f"\\n\\nYou are speaking with {user_name}."

    return base_prompt
