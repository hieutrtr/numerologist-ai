# Voice Pipeline Technical Specification

**Version:** 1.0
**Last Updated:** 2025-11-30
**Framework:** Pipecat v0.0.93
**Language:** Domain-Agnostic (Reusable Template)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Details](#component-details)
4. [Pipeline Flow](#pipeline-flow)
5. [Configuration](#configuration)
6. [Performance Characteristics](#performance-characteristics)
7. [Integration Guide](#integration-guide)
8. [Code Examples](#code-examples)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Overview

### What is This Pipeline?

This is a production-ready voice AI pipeline built with **Pipecat**, designed to enable real-time voice conversations between users and AI assistants. The pipeline handles the complete voice interaction cycle:

```
User Speech → Speech-to-Text → Language Model → Text-to-Speech → User Speakers
```

### Key Features

- **Real-time Processing**: Sub-1-second end-to-end latency
- **Multilingual Support**: 8+ languages (English, Vietnamese, Spanish, French, German, Japanese, Chinese, Portuguese)
- **Async Architecture**: Non-blocking I/O using Python asyncio
- **WebRTC Transport**: Low-latency audio streaming via Daily.co
- **Function Calling**: AI can invoke custom business logic during conversations
- **Context Management**: Automatic conversation history tracking
- **Production-Ready**: Comprehensive error handling and logging

### Use Cases

- Voice-enabled chatbots and virtual assistants
- Interactive voice response (IVR) systems
- Voice-based data entry and form filling
- Real-time translation services
- Accessibility tools for voice interaction
- Educational tutoring systems
- Customer support automation

---

## Architecture

### System Architecture Diagram

```
┌─────────────┐
│    User     │ 🎤 Microphone
│  (Browser)  │ 🔊 Speakers
└──────┬──────┘
       │ WebRTC (Opus 48kHz)
       ↓
┌──────────────────────────────────────────────────────────────┐
│                    Daily.co Infrastructure                    │
│  • WebRTC Signaling (TURN/STUN)                              │
│  • Room Management API                                        │
│  • JWT Token Authentication                                   │
└──────────────┬───────────────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────────────┐
│               Pipecat Voice Pipeline (asyncio)                │
│                                                               │
│  transport.input()                                            │
│       ↓                                                       │
│  [Silero VAD] ← Optional voice activity detection            │
│       ↓                                                       │
│  [Azure Speech STT] ← Speech-to-Text (nova-3-general)        │
│       ↓                                                       │
│  context_aggregator.user() ← Collect user message            │
│       ↓                                                       │
│  [Azure OpenAI LLM] ← GPT-5-mini language model              │
│       ↓ ↔ [Custom Functions] ← Business logic                │
│       ↓                                                       │
│  [ElevenLabs TTS] ← Text-to-Speech (turbo_v2_5)              │
│       ↓                                                       │
│  transport.output()                                           │
│       ↓                                                       │
│  context_aggregator.assistant() ← Store AI response          │
│                                                               │
└──────────────┬───────────────────────────────────────────────┘
               │
               ↓
    ┌──────────────────────┐
    │  External AI Services │
    ├──────────────────────┤
    │  • Azure Speech STT   │
    │  • Azure OpenAI LLM   │
    │  • ElevenLabs TTS     │
    └──────────────────────┘
```

### Integration Architecture

```
┌─────────────────┐         REST API          ┌──────────────────┐
│   Frontend App  │ ─────────────────────────> │   Backend API    │
│  (React/Next.js)│                            │    (FastAPI)     │
│                 │ <─────────────────────────  │                  │
└────────┬────────┘    Room URL + Token        └────────┬─────────┘
         │                                               │
         │ WebRTC                                        │ Spawn Task
         │ (User connects)                               │ asyncio.create_task()
         ↓                                               ↓
    ┌─────────────────────────────────────────────────────────┐
    │              Daily.co Room (WebRTC)                     │
    │  • User joins as participant                            │
    │  • Bot joins as participant                             │
    │  • Real-time bidirectional audio streaming              │
    └─────────────────────────────────────────────────────────┘
```

**Key Points:**

1. **Frontend** and **Bot** both connect to the same Daily.co room
2. **Backend** orchestrates but doesn't handle media streams directly
3. **Voice Pipeline** runs as a background asyncio task
4. **WebRTC** handles all real-time audio transmission
5. **Bot** appears as another participant in the call

---

## Component Details

### 1. Daily.co WebRTC Transport

**Purpose:** Handles real-time audio streaming between user and bot

**Technology:**
- Protocol: WebRTC (Web Real-Time Communication)
- Audio Codec: Opus (48kHz, 48kbps)
- Transport Library: `pipecat.transports.daily`

**Configuration:**

```python
from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.audio.vad.silero import SileroVADAnalyzer

transport = DailyTransport(
    room_url="https://yourdomain.daily.co/room-name",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # JWT meeting token
    bot_name="AI Assistant",
    params=DailyParams(
        audio_in_enabled=True,   # Receive audio from user
        audio_out_enabled=True,  # Send audio to user
        vad_analyzer=SileroVADAnalyzer()  # Optional: Voice Activity Detection
    )
)
```

**Key Features:**
- Low-latency audio streaming (<100ms network latency)
- Automatic reconnection on network failures
- Cross-platform support (browser, mobile, desktop)
- TURN/STUN server management for NAT traversal

### 2. Voice Activity Detection (VAD) - Optional

**Purpose:** Detect when user is speaking to reduce false triggers

**Technology:** Silero VAD (ML-based voice detection)

**Configuration:**

```python
from pipecat.audio.vad.silero import SileroVADAnalyzer, VADParams

vad_analyzer = SileroVADAnalyzer(
    params=VADParams(
        min_volume=0.5,      # Audio volume threshold (0-1)
        start_secs=0.15,     # Time before confirming speech start
        stop_secs=0.6,       # Silence duration before speech end
        confidence=0.7,      # Speech detection confidence (0-1)
    )
)
```

**Performance Tuning:**
- **Lower `start_secs`** (0.1-0.2s): Faster detection, more sensitive
- **Higher `stop_secs`** (0.8-1.0s): Better for slow speakers, higher latency
- **Higher `min_volume`** (0.6-0.8): Reduce background noise false positives
- **Higher `confidence`** (0.8-0.9): More accurate detection, may miss quiet speech

**When to Use VAD:**
- ✅ Noisy environments (background music, multiple speakers)
- ✅ Reducing interruption false positives
- ❌ Very quiet speakers (may miss speech)
- ❌ When minimum latency is critical (<1s target)

### 3. Speech-to-Text (STT) Service

**Purpose:** Convert user audio to text transcription

**Supported Services:**
- **Azure Speech Services** (Currently used)
- **Deepgram** (Legacy, replaced in v1.0)
- **OpenAI Whisper**
- **Google Speech-to-Text**

**Azure Speech STT Configuration:**

```python
from pipecat.services.azure.stt import AzureSTTService
from pipecat.transcriptions.language import Language

stt = AzureSTTService(
    api_key=os.getenv("AZURE_SPEECH_API_KEY"),
    region="eastus",  # Azure region
    language=Language.EN_US  # Language.VI for Vietnamese, etc.
)
```

**Supported Languages:**
```python
Language.EN_US   # English (US)
Language.VI      # Vietnamese
Language.ES      # Spanish
Language.FR      # French
Language.DE      # German
Language.JA      # Japanese
Language.ZH      # Chinese
Language.PT      # Portuguese
```

**Performance:**
- Latency: 200-300ms (from audio to text)
- Accuracy: 95%+ for clear speech
- Interim Results: Enabled (real-time streaming transcription)

**Deepgram STT Configuration (Legacy):**

```python
from pipecat.services.deepgram.stt import DeepgramSTTService, LiveOptions

stt = DeepgramSTTService(
    api_key=os.getenv("DEEPGRAM_API_KEY"),
    live_options=LiveOptions(
        language="en-US",
        model="nova-3-general",
        endpointing=300,        # Endpoint detection (ms)
        utterance_end_ms=1000,  # Silence before finalizing transcript
        interim_results=True,   # Stream partial results
        punctuate=True,
        smart_format=True,
    )
)
```

### 4. Language Model (LLM) Service

**Purpose:** Generate intelligent responses to user input

**Supported Services:**
- **Azure OpenAI** (Currently used)
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic Claude**
- **Google Gemini**

**Azure OpenAI Configuration:**

```python
from pipecat.services.azure.llm import AzureLLMService
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

llm = AzureLLMService(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model="gpt-5-mini",  # Deployment name in Azure
    api_version="2024-05-01",
    run_in_parallel=False  # Sequential function calling
)

# Initialize conversation context
system_prompt = "You are a friendly AI assistant. Help the user with their questions."
messages = [{"role": "system", "content": system_prompt}]
llm_context = OpenAILLMContext(messages=messages)
```

**Function Calling:**

Register custom functions that the AI can invoke:

```python
def handle_get_weather(location: str) -> dict:
    """Get weather for a location."""
    # Your business logic here
    return {"temperature": 72, "condition": "sunny"}

llm.register_function(
    "get_weather",
    handle_get_weather,
    cancel_on_interruption=False  # Continue execution if user interrupts
)
```

**Performance:**
- Latency: 300-500ms (depends on model size)
- Context Window: 128K tokens (GPT-5-mini)
- Streaming: Enabled (real-time response generation)

### 5. Text-to-Speech (TTS) Service

**Purpose:** Convert AI response text to natural speech audio

**Supported Services:**
- **ElevenLabs** (Currently used - best quality)
- **Azure Speech TTS**
- **OpenAI TTS**
- **Google Text-to-Speech**

**ElevenLabs TTS Configuration:**

```python
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService

tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Voice selection
    model="eleven_turbo_v2_5",  # Fastest model with multilingual support
)
```

**Voice Selection:**
- Browse voices at: https://elevenlabs.io/voice-library
- Preview voices before selection
- Voice ID format: 21-character alphanumeric string

**Performance:**
- Latency: 200-300ms (from text to audio)
- Quality: Near-human voice quality
- Streaming: Enabled (audio plays while generating)

### 6. Context Aggregators

**Purpose:** Manage conversation history and message flow

**Architecture:**

```python
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

# Create context with message history
llm_context = OpenAILLMContext(
    messages=[
        {"role": "system", "content": "System prompt here"},
        {"role": "user", "content": "Previous user message"},
        {"role": "assistant", "content": "Previous AI response"}
    ]
)

# Create aggregators using LLM service
context_aggregator = llm.create_context_aggregator(llm_context)

# In pipeline:
# - context_aggregator.user() collects user transcripts
# - context_aggregator.assistant() stores AI responses
```

**Benefits:**
- Automatic message history management
- Proper function call result handling
- Conversation context persistence
- Memory-efficient message storage

---

## Pipeline Flow

### Complete Data Flow

```
Step 1: User speaks into microphone
   ↓ (WebRTC audio stream - Opus 48kHz)
Step 2: Daily.co receives audio, sends to bot
   ↓ (PCM audio - 16kHz)
Step 3: [Optional] Silero VAD detects voice activity
   ↓ (Voice segments)
Step 4: Azure Speech STT transcribes to text
   ↓ (UTF-8 text string)
Step 5: User Context Aggregator adds to history
   ↓ (OpenAI messages JSON array)
Step 6: Azure OpenAI LLM processes with system prompt
   ↓ (May call custom functions)
   ↔ Custom Functions execute business logic
   ↓ (Function results return to LLM)
Step 7: LLM generates response text
   ↓ (Response text string)
Step 8: Assistant Context Aggregator stores response
   ↓ (Text to synthesize)
Step 9: ElevenLabs TTS converts to speech audio
   ↓ (MP3 audio stream)
Step 10: Daily.co sends audio to user
   ↓ (WebRTC audio stream)
Step 11: User hears response through speakers
```

### Pipeline Component Order

**Critical:** Component order in the pipeline array is essential:

```python
pipeline = Pipeline([
    transport.input(),              # 1. Audio from user
    stt,                            # 2. Speech-to-text
    context_aggregator.user(),      # 3. Collect user message
    llm,                            # 4. Generate response
    tts,                            # 5. Text-to-speech
    transport.output(),             # 6. Audio to user
    context_aggregator.assistant(), # 7. Store assistant message
])
```

**Why This Order?**
1. Audio must be transcribed before processing
2. User message must be added to context before LLM
3. LLM response must be synthesized to audio
4. Audio must be sent before storing response
5. Assistant message stored for next conversation turn

### Async Execution

The pipeline runs as an asyncio task:

```python
import asyncio
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner

# Create task
task = PipelineTask(
    pipeline,
    params=PipelineParams()
)

# Run pipeline (non-blocking)
runner = PipelineRunner()
await runner.run(task)  # Runs until stopped or room closes
```

---

## Configuration

### Environment Variables

```bash
# Daily.co WebRTC (required)
DAILY_API_KEY=your_daily_api_key_here

# Azure Speech Services - STT (required)
AZURE_SPEECH_API_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus

# Azure OpenAI - LLM (required)
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=gpt-5-mini
AZURE_OPENAI_API_VERSION=2024-05-01

# ElevenLabs - TTS (required)
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL=eleven_turbo_v2_5

# Application Settings (optional)
VOICE_LANGUAGE=en  # Language code (en, vi, es, fr, de, ja, zh, pt)
```

### Application Settings (Python)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Daily.co
    daily_api_key: str

    # Azure Speech
    azure_speech_api_key: str
    azure_speech_region: str = "eastus"

    # Azure OpenAI
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_model_deployment_name: str = "gpt-5-mini"
    azure_openai_api_version: str = "2024-05-01"

    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    elevenlabs_model: str = "eleven_turbo_v2_5"

    # Application
    voice_language: str = "en"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Performance Characteristics

### Latency Breakdown

| Component           | Target Latency | Notes                              |
|---------------------|----------------|------------------------------------|
| WebRTC Network      | 50-100ms       | Depends on user's internet         |
| Silero VAD (opt)    | 150-250ms      | Voice detection time               |
| Azure Speech STT    | 200-300ms      | Audio → Text transcription         |
| Azure OpenAI LLM    | 300-500ms      | Text → Response generation         |
| ElevenLabs TTS      | 200-300ms      | Text → Audio synthesis             |
| WebRTC Network      | 50-100ms       | Audio back to user                 |
| **Total**           | **<1 second**  | End-to-end user experience         |

### Optimization Strategies

**1. Reduce VAD Latency:**
```python
VADParams(
    start_secs=0.1,   # Faster detection (default: 0.25)
    stop_secs=0.5,    # Quicker endpoint (default: 1.0)
)
```

**2. Use Faster LLM Model:**
- GPT-5-mini (fastest, good quality)
- GPT-4-turbo (slower, best quality)

**3. Enable Streaming:**
- All services (STT, LLM, TTS) support streaming by default
- Audio plays while generating (perceived latency <500ms)

**4. Optimize System Prompt:**
- Keep system prompts concise (<500 words)
- Reduce token usage = faster LLM responses

**5. Regional Configuration:**
- Deploy Azure services in same region as users
- Use closest Daily.co edge server

### Resource Usage

**Memory:**
- Base pipeline: ~200MB
- With conversation history (100 messages): ~300MB
- Peak during audio processing: ~400MB

**CPU:**
- Idle: 5-10% (1 core)
- Active conversation: 30-50% (1 core)
- Concurrent users: Scale horizontally (1 core per 2-3 users)

**Network:**
- Upload: 48kbps (Opus audio to user)
- Download: 48kbps (Opus audio from user)
- Total per user: ~100kbps bidirectional

---

## Integration Guide

### Backend Integration (FastAPI Example)

**Step 1: Install Dependencies**

```bash
pip install pipecat-ai[daily,azure,elevenlabs]
pip install fastapi uvicorn python-dotenv pydantic-settings
```

**Step 2: Create Voice Service**

```python
# services/daily_service.py
import os
import httpx

async def create_room(room_name: str) -> dict:
    """Create Daily.co room and generate meeting token."""
    async with httpx.AsyncClient() as client:
        # Create room
        response = await client.post(
            "https://api.daily.co/v1/rooms",
            headers={
                "Authorization": f"Bearer {os.getenv('DAILY_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "name": room_name,
                "properties": {
                    "enable_screenshare": False,
                    "enable_chat": False,
                    "start_video_off": True,
                    "start_audio_off": False
                }
            }
        )
        room_data = response.json()

        # Generate meeting token
        token_response = await client.post(
            "https://api.daily.co/v1/meeting-tokens",
            headers={
                "Authorization": f"Bearer {os.getenv('DAILY_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "properties": {
                    "room_name": room_name,
                    "is_owner": False
                }
            }
        )
        token_data = token_response.json()

        return {
            "room_url": room_data["url"],
            "room_name": room_name,
            "meeting_token": token_data["token"]
        }
```

**Step 3: Create Pipecat Bot**

```python
# voice_pipeline/bot.py
import asyncio
from typing import Optional
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.azure.llm import AzureLLMService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.transcriptions.language import Language

async def run_bot(
    room_url: str,
    token: str,
    system_prompt: Optional[str] = None
) -> PipelineTask:
    """Run voice AI bot in Daily.co room."""

    # Configure transport
    transport = DailyTransport(
        room_url,
        token,
        "AI Assistant",
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer()
        )
    )

    # Initialize services
    stt = AzureSTTService(
        api_key=os.getenv("AZURE_SPEECH_API_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION"),
        language=Language.EN_US
    )

    llm = AzureLLMService(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model=os.getenv("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        model=os.getenv("ELEVENLABS_MODEL")
    )

    # Initialize conversation context
    if not system_prompt:
        system_prompt = "You are a friendly AI assistant."

    messages = [{"role": "system", "content": system_prompt}]
    llm_context = OpenAILLMContext(messages=messages)
    context_aggregator = llm.create_context_aggregator(llm_context)

    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant()
    ])

    # Run pipeline
    task = PipelineTask(pipeline, params=PipelineParams())
    runner = PipelineRunner()
    await runner.run(task)

    return task
```

**Step 4: Create API Endpoint**

```python
# main.py
from fastapi import FastAPI
import asyncio
from services.daily_service import create_room
from voice_pipeline.bot import run_bot

app = FastAPI()

@app.post("/api/v1/voice/start-call")
async def start_voice_call():
    """Create room and spawn bot."""
    # Create Daily.co room
    room_info = await create_room(f"call-{uuid.uuid4()}")

    # Spawn bot in background
    asyncio.create_task(
        run_bot(
            room_info["room_url"],
            room_info["meeting_token"]
        )
    )

    return {
        "room_url": room_info["room_url"],
        "meeting_token": room_info["meeting_token"]
    }
```

### Frontend Integration (React Example)

```typescript
// hooks/useVoiceCall.ts
import { useDaily } from '@daily-co/daily-react';
import { useState } from 'react';

export const useVoiceCall = () => {
  const daily = useDaily();
  const [isInCall, setIsInCall] = useState(false);

  const startCall = async () => {
    // Request room from backend
    const response = await fetch('/api/v1/voice/start-call', {
      method: 'POST'
    });
    const { room_url, meeting_token } = await response.json();

    // Join Daily.co room
    await daily?.join({
      url: room_url,
      token: meeting_token
    });

    setIsInCall(true);
  };

  const endCall = async () => {
    await daily?.leave();
    setIsInCall(false);
  };

  return { startCall, endCall, isInCall };
};
```

```tsx
// components/VoiceCallButton.tsx
import { useVoiceCall } from '../hooks/useVoiceCall';

export const VoiceCallButton = () => {
  const { startCall, endCall, isInCall } = useVoiceCall();

  return (
    <button onClick={isInCall ? endCall : startCall}>
      {isInCall ? '🔇 End Call' : '🎤 Start Voice Call'}
    </button>
  );
};
```

---

## Code Examples

### Example 1: Basic Voice Bot

```python
import asyncio
import os
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.transports.daily.transport import DailyTransport, DailyParams
from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.azure.llm import AzureLLMService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.transcriptions.language import Language

async def main():
    # Setup services
    transport = DailyTransport(
        "https://yourdomain.daily.co/test-room",
        "your_jwt_token_here",
        "AI Assistant",
        DailyParams(audio_in_enabled=True, audio_out_enabled=True)
    )

    stt = AzureSTTService(
        api_key=os.getenv("AZURE_SPEECH_API_KEY"),
        region="eastus",
        language=Language.EN_US
    )

    llm = AzureLLMService(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        model="gpt-5-mini",
        api_version="2024-05-01"
    )

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model="eleven_turbo_v2_5"
    )

    # Setup context
    messages = [{
        "role": "system",
        "content": "You are a helpful AI assistant."
    }]
    llm_context = OpenAILLMContext(messages=messages)
    context_aggregator = llm.create_context_aggregator(llm_context)

    # Build pipeline
    pipeline = Pipeline([
        transport.input(),
        stt,
        context_aggregator.user(),
        llm,
        tts,
        transport.output(),
        context_aggregator.assistant()
    ])

    # Run
    task = PipelineTask(pipeline, params=PipelineParams())
    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Bot with Function Calling

```python
# Define custom functions
def get_current_time() -> dict:
    """Get current time."""
    from datetime import datetime
    return {
        "time": datetime.now().strftime("%I:%M %p"),
        "timezone": "UTC"
    }

def search_database(query: str) -> dict:
    """Search database for information."""
    # Your database query logic here
    return {
        "results": ["Result 1", "Result 2"],
        "count": 2
    }

# Register with LLM
llm.register_function("get_current_time", get_current_time)
llm.register_function("search_database", search_database)

# Define tools for LLM context
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search the database for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Create context with tools
llm_context = OpenAILLMContext(messages=messages, tools=tools)
```

### Example 3: Multilingual Bot

```python
# Language mapping
language_map = {
    "en": Language.EN_US,
    "vi": Language.VI,
    "es": Language.ES,
    "fr": Language.FR,
    "de": Language.DE,
    "ja": Language.JA,
    "zh": Language.ZH,
    "pt": Language.PT,
}

# Language-specific system prompts
system_prompts = {
    "en": "You are a friendly AI assistant. How can I help you today?",
    "vi": "Bạn là một trợ lý AI thân thiện. Tôi có thể giúp gì cho bạn?",
    "es": "Eres un asistente de IA amigable. ¿Cómo puedo ayudarte hoy?",
    "fr": "Vous êtes un assistant IA amical. Comment puis-je vous aider?",
}

# Configure for specific language
user_language = "vi"  # Vietnamese
language_enum = language_map.get(user_language, Language.EN_US)
system_prompt = system_prompts.get(user_language, system_prompts["en"])

stt = AzureSTTService(
    api_key=os.getenv("AZURE_SPEECH_API_KEY"),
    region="eastus",
    language=language_enum
)

messages = [{"role": "system", "content": system_prompt}]
```

---

## Troubleshooting

### Common Issues

#### 1. Bot Not Joining Room

**Symptoms:**
- Bot doesn't appear as participant in Daily.co room
- No audio received from bot

**Causes & Solutions:**

```python
# Check 1: Verify API key is correct
daily_api_key = os.getenv("DAILY_API_KEY")
if not daily_api_key:
    raise ValueError("DAILY_API_KEY not set")

# Check 2: Verify room URL format
# Correct: https://yourdomain.daily.co/room-name
# Incorrect: yourdomain.daily.co/room-name (missing https://)

# Check 3: Verify token is valid JWT
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)  # Should contain room_name

# Check 4: Check bot is running
# Add logging:
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. High Latency (>2 seconds)

**Diagnosis:**

```python
import time

# Measure component latencies
start = time.time()
# ... component execution ...
print(f"Component took: {time.time() - start:.3f}s")
```

**Solutions:**

1. **Reduce VAD detection time:**
```python
VADParams(start_secs=0.1, stop_secs=0.5)
```

2. **Use faster LLM model:**
```python
model="gpt-5-mini"  # Instead of "gpt-4"
```

3. **Optimize system prompt (reduce tokens):**
```python
# Bad: 500-word detailed prompt
# Good: 50-word concise prompt
```

4. **Check network latency:**
```bash
ping api.daily.co
# Should be <50ms
```

#### 3. Speech Not Recognized

**Symptoms:**
- User speaks but bot doesn't respond
- STT not transcribing correctly

**Solutions:**

1. **Check microphone permissions:**
```typescript
// Frontend
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
```

2. **Verify language configuration:**
```python
# Make sure language matches user's speech
language=Language.EN_US  # For English speakers
```

3. **Adjust VAD sensitivity:**
```python
VADParams(
    min_volume=0.3,  # Lower threshold (more sensitive)
    confidence=0.6   # Lower confidence (less strict)
)
```

4. **Check audio quality:**
```python
# Enable debug logging
logging.getLogger("pipecat").setLevel(logging.DEBUG)
```

#### 4. Bot Interrupts Itself

**Symptoms:**
- Bot stops speaking mid-sentence
- Premature interruptions

**Causes:**
- VAD detecting bot's own audio as user speech
- Acoustic echo

**Solutions:**

1. **Disable VAD in DailyParams:**
```python
DailyParams(
    audio_in_enabled=True,
    audio_out_enabled=True,
    vad_analyzer=None  # Disable VAD
)
```

2. **Use text-based interruption detection:**
```python
from pipecat.audio.interruptions.min_words_interruption_strategy import MinWordsInterruptionStrategy

task = PipelineTask(
    pipeline,
    params=PipelineParams(
        allow_interruptions=True,
        interruption_strategies=[
            MinWordsInterruptionStrategy(min_words=2)
        ]
    )
)
```

#### 5. API Rate Limits

**Symptoms:**
- 429 errors from external services
- Slow responses during high traffic

**Solutions:**

1. **Implement rate limiting:**
```python
import asyncio
from collections import deque

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    async def acquire(self):
        now = asyncio.get_event_loop().time()
        while self.calls and self.calls[0] <= now - self.period:
            self.calls.popleft()

        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            await asyncio.sleep(sleep_time)

        self.calls.append(now)

# Usage
rate_limiter = RateLimiter(max_calls=10, period=1.0)  # 10 calls/second
await rate_limiter.acquire()
```

2. **Use caching for repeated requests:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(key: str):
    # Your expensive operation
    pass
```

3. **Scale horizontally (multiple bot instances):**
```bash
# Run multiple backend instances
uvicorn main:app --workers 4
```

---

## API Reference

### Core Classes

#### `DailyTransport`

```python
DailyTransport(
    room_url: str,              # Daily.co room URL
    token: str,                 # JWT meeting token
    bot_name: str,              # Bot display name
    params: DailyParams         # Transport parameters
)
```

#### `DailyParams`

```python
DailyParams(
    audio_in_enabled: bool = True,        # Receive audio from room
    audio_out_enabled: bool = True,       # Send audio to room
    vad_analyzer: Optional[VADAnalyzer] = None  # Voice activity detection
)
```

#### `AzureSTTService`

```python
AzureSTTService(
    api_key: str,              # Azure Speech API key
    region: str,               # Azure region (e.g., "eastus")
    language: Language         # Language enum (Language.EN_US, etc.)
)
```

#### `AzureLLMService`

```python
AzureLLMService(
    api_key: str,              # Azure OpenAI API key
    endpoint: str,             # Azure OpenAI endpoint URL
    model: str,                # Deployment name
    api_version: str = "2024-05-01",  # API version
    run_in_parallel: bool = False     # Sequential function calling
)
```

#### `ElevenLabsTTSService`

```python
ElevenLabsTTSService(
    api_key: str,              # ElevenLabs API key
    voice_id: str,             # Voice selection ID
    model: str = "eleven_turbo_v2_5"  # TTS model
)
```

#### `OpenAILLMContext`

```python
OpenAILLMContext(
    messages: List[dict],      # Message history
    tools: Optional[List[dict]] = None  # Function definitions
)
```

#### `Pipeline`

```python
Pipeline(
    processors: List[Processor]  # Ordered list of pipeline components
)
```

#### `PipelineTask`

```python
PipelineTask(
    pipeline: Pipeline,        # Pipeline to execute
    params: PipelineParams     # Task parameters
)
```

---

## Appendix

### File Structure

```
project/
├── .env                          # Environment variables
├── main.py                       # FastAPI application entry
├── services/
│   ├── __init__.py
│   ├── daily_service.py         # Daily.co room management
│   └── voice_service.py         # Voice orchestration
├── voice_pipeline/
│   ├── __init__.py
│   ├── bot.py                   # Pipecat bot implementation
│   ├── function_handlers.py    # Custom function implementations
│   └── system_prompts.py        # System prompt templates
└── docs/
    └── voice-pipeline-technical-specification.md
```

### Dependencies

```txt
# Core framework
pipecat-ai[daily,azure,elevenlabs]==0.0.93

# Web framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Configuration
python-dotenv==1.0.0
pydantic-settings==2.1.0

# Async HTTP
httpx==0.26.0

# Database (optional)
sqlmodel==0.0.14
asyncpg==0.29.0  # For PostgreSQL
```

### External Service Pricing (2025 Estimates)

| Service        | Tier          | Pricing                          |
|----------------|---------------|----------------------------------|
| Daily.co       | Free          | 10,000 minutes/month             |
| Daily.co       | Paid          | $0.0015/min/participant          |
| Azure Speech   | Free          | 5 hours/month                    |
| Azure Speech   | Paid          | $1.00/hour                       |
| Azure OpenAI   | Pay-as-you-go | $0.30/1M input tokens (GPT-5)    |
| ElevenLabs     | Free          | 10,000 characters/month          |
| ElevenLabs     | Paid          | $5/month (30,000 chars)          |

---

## Contributing

This specification is maintained as a living document. To contribute:

1. Fork the repository
2. Create a feature branch
3. Update documentation with examples
4. Submit pull request

---

## License

This technical specification is provided as-is under MIT License. Use at your own discretion.

---

## Support

For questions or issues:
- Pipecat Documentation: https://docs.pipecat.ai/
- Daily.co Docs: https://docs.daily.co/
- Azure Speech Docs: https://learn.microsoft.com/azure/ai-services/speech-service/
- Azure OpenAI Docs: https://learn.microsoft.com/azure/ai-services/openai/
- ElevenLabs Docs: https://docs.elevenlabs.io/

---

**Last Updated:** 2025-11-30
**Version:** 1.0
**Author:** Voice Pipeline Team
