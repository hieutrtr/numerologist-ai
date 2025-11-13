# Voice Pipeline Technical Specification
## Numerologist AI Voice Bot Architecture

### Table of Contents
1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Services Integration](#services-integration)
4. [Function Calling System](#function-calling-system)
5. [Context Aggregation](#context-aggregation)
6. [Frontend Audio Integration](#frontend-audio-integration)
7. [Error Handling & Recovery](#error-handling--recovery)
8. [Testing Strategy](#testing-strategy)

---

## Overview

The Numerologist AI Voice Bot implements a real-time voice conversation pipeline using the Pipecat framework, enabling users to interact naturally with an AI numerology expert through speech. The system processes voice input, performs numerology calculations via function calling, and responds with synthesized speech in multiple languages (English and Vietnamese).

### Core Technologies
- **Pipecat Framework**: Orchestrates the voice pipeline
- **Daily.co**: WebRTC transport for real-time audio
- **Deepgram**: Speech-to-text transcription
- **Azure OpenAI GPT-4**: Language understanding and response generation
- **ElevenLabs**: Natural text-to-speech synthesis

### Data Flow
```
User Voice → WebRTC → STT → LLM → Function Calls → TTS → WebRTC → User Audio
```

---

## Pipeline Architecture

### Pipeline Components

The voice pipeline (`backend/src/voice_pipeline/pipecat_bot.py`) consists of seven sequential stages:

```python
pipeline = Pipeline([
    transport.input(),              # 1. Audio from user (WebRTC)
    stt,                           # 2. Speech-to-text (Deepgram)
    context_aggregator.user(),     # 3. Collect user message
    llm,                          # 4. Generate response (Azure OpenAI)
    tts,                          # 5. Text-to-speech (ElevenLabs)
    transport.output(),           # 6. Audio to user (WebRTC)
    context_aggregator.assistant(), # 7. Store assistant message
])
```

### Component Responsibilities

#### 1. Transport Input (Daily.co)
- Receives raw audio stream from user's microphone via WebRTC
- Handles Voice Activity Detection (VAD) using SileroVADAnalyzer
- Manages connection state and audio quality

#### 2. Speech-to-Text (Deepgram)
- Converts audio to text with language-specific models
- Supports multiple languages: en, vi, es, fr, de, ja, zh, pt
- Configuration:
  ```python
  DeepgramSTTService(
      language=Language.VI,  # Dynamic based on settings
      model="nova-3-general",
      vad_events=True,
      endpointing=True,
      interim_results=True,
      punctuate=True,
      smart_format=True
  )
  ```

#### 3. User Context Aggregator
- Captures transcribed user messages
- Maintains conversation history
- Ensures proper message ordering

#### 4. Language Model (Azure OpenAI)
- Processes user intent
- Decides when to call numerology functions
- Generates contextual responses
- Configuration:
  ```python
  AzureLLMService(
      model="gpt-4",
      run_in_parallel=False  # Sequential function calling
  )
  ```

#### 5. Text-to-Speech (ElevenLabs)
- Converts LLM responses to natural speech
- Maintains voice consistency
- Supports multiple voice profiles

#### 6. Transport Output
- Streams synthesized audio back to user
- Manages audio buffering and playback

#### 7. Assistant Context Aggregator
- Stores AI responses in conversation history
- Tracks function call results
- Maintains context for follow-up questions

---

## Services Integration

### Service Initialization Pattern

Each service follows a consistent initialization pattern:

```python
# 1. Validate API keys (lazy validation)
_validate_configuration()

# 2. Configure transport with VAD
transport = DailyTransport(
    room_url, token, "Numerology AI Bot",
    DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer()
    )
)

# 3. Initialize speech services
stt = DeepgramSTTService(api_key=..., live_options=...)
llm = AzureLLMService(api_key=..., endpoint=...)
tts = ElevenLabsTTSService(api_key=..., voice_id=...)

# 4. Register function handlers
llm.register_function("calculate_life_path", handler)

# 5. Create context with tools
llm_context = OpenAILLMContext(messages=..., tools=...)

# 6. Create aggregator from LLM service
context_aggregator = llm.create_context_aggregator(llm_context)
```

### Daily.co Room Management

Room lifecycle (`backend/src/services/daily_service.py`):

```python
async def create_room(unique_id: str) -> dict:
    # Creates WebRTC room with 2-hour expiry
    # Returns: room_url, room_name, meeting_token

async def delete_room(room_id: str) -> bool:
    # Best-effort cleanup (rooms auto-expire)
```

### Environment Configuration

Required environment variables (`backend/src/core/settings.py`):

```env
# Speech Services
DEEPGRAM_API_KEY=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=gpt-4
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=

# Daily.co
DAILY_API_KEY=
DAILY_API_URL=https://api.daily.co/v1

# Language Settings
VOICE_LANGUAGE=vi  # or en, es, fr, etc.
```

---

## Function Calling System

### Architecture Overview

The function calling system enables the LLM to execute numerology calculations during conversation:

```
User Query → LLM Decision → Function Call → Handler Execution → Result Callback → LLM Response
```

### Function Schema Definition

Functions are defined using Pipecat's `FunctionSchema` (`backend/src/voice_pipeline/numerology_functions.py`):

```python
calculate_life_path_function = FunctionSchema(
    name="calculate_life_path",
    description="Calculate the user's Life Path number from their birth date...",
    properties={
        "birth_date": {
            "type": "string",
            "description": "User's birth date in YYYY-MM-DD format"
        }
    },
    required=["birth_date"]
)
```

### OpenAI Format Conversion

Since OpenAILLMContext expects JSON format, we convert:

```python
def _function_schema_to_openai_format(func_schema: FunctionSchema) -> dict:
    return {
        "type": "function",
        "function": {
            "name": func_schema.name,
            "description": func_schema.description,
            "parameters": {
                "type": "object",
                "properties": func_schema.properties,
                "required": func_schema.required
            }
        }
    }
```

### Function Handler Pattern

Handlers follow async callback pattern (`backend/src/voice_pipeline/function_handlers.py`):

```python
async def handle_calculate_life_path(params: FunctionCallParams):
    try:
        # 1. Extract arguments
        birth_date = params.arguments.get("birth_date")

        # 2. Parse and validate
        parsed_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # 3. Execute calculation
        result = calculate_life_path(parsed_date)

        # 4. Return via callback with run_llm flag
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback(
            {"life_path_number": result},
            properties=properties
        )
    except Exception as e:
        await params.result_callback({
            "error": "CalculationError",
            "message": "Unable to calculate"
        })
```

### Function Registration

Functions are registered with the LLM service:

```python
llm.register_function("calculate_life_path", handle_calculate_life_path,
                     cancel_on_interruption=False)
```

### Available Functions

1. **calculate_life_path**: Calculates Life Path number from birth date
2. **calculate_expression_number**: Calculates Expression number from full name
3. **calculate_soul_urge_number**: Calculates Soul Urge number from full name
4. **get_numerology_interpretation**: Retrieves interpretations from database

---

## Context Aggregation

### Context Management Strategy

The context aggregator maintains conversation history and function results:

```python
# Create aggregator from LLM service (critical for function calling)
context_aggregator = llm.create_context_aggregator(llm_context)

# Use in pipeline
pipeline = Pipeline([
    ...
    context_aggregator.user(),      # Capture user messages
    llm,                            # Process with context
    ...
    context_aggregator.assistant()  # Capture assistant + function results
])
```

### Why LLM-Created Aggregator?

Using `llm.create_context_aggregator()` instead of separate aggregators ensures:
1. Function call results are properly added to context
2. Conversation history includes tool responses
3. Prevents infinite function calling loops
4. Maintains proper message ordering

### Context Structure

```python
llm_context = OpenAILLMContext(
    messages=[
        {
            "role": "system",
            "content": system_prompt  # Vietnamese or English
        }
    ],
    tools=numerology_tools  # Function definitions
)
```

### System Prompt Management

Language-specific prompts (`backend/src/voice_pipeline/system_prompts.py`):

```python
def get_numerology_system_prompt(user: User) -> str:
    # Vietnamese numerology expert prompt with:
    # - User personalization
    # - Numerology knowledge sections
    # - Function calling instructions
    # - Conversation guidelines
```

---

## Frontend Audio Integration

### Mobile Audio Pipeline (React Native)

#### 1. Microphone Permissions
```typescript
// mobile/src/hooks/usePermissions.ts
const requestMicrophonePermission = async () => {
  const { status } = await Audio.requestPermissionsAsync();
  return status === 'granted';
};
```

#### 2. Daily.co WebRTC Integration
```typescript
// mobile/src/services/daily.ts
import Daily from '@daily-co/react-native-daily-js';

const call = Daily.createCallObject({
  audioSource: true,
  videoSource: false
});

await call.join({
  url: roomUrl,
  token: meetingToken
});
```

#### 3. Audio State Management
```typescript
// mobile/src/store/conversationStore.ts
interface ConversationState {
  isConnected: boolean;
  isMuted: boolean;
  isRecording: boolean;
  transcription: string;
  botResponse: string;
}
```

#### 4. Voice Activity Visualization
```typescript
// mobile/src/components/VoiceVisualizer.tsx
// Real-time audio amplitude visualization
// WebRTC audio track analysis
```

### API Integration Flow

```typescript
// 1. Start conversation
const response = await api.post('/conversations/start');
const { conversation_id, daily_room_url, daily_token } = response.data;

// 2. Join Daily room
await call.join({ url: daily_room_url, token: daily_token });

// 3. Handle audio events
call.on('track-started', handleTrackStarted);
call.on('track-stopped', handleTrackStopped);

// 4. End conversation
await api.post(`/conversations/${conversation_id}/end`);
await call.leave();
```

---

## Error Handling & Recovery

### Pipeline Error Boundaries

```python
try:
    # Pipeline initialization
    await runner.run(task)
except ValueError as e:
    # Configuration errors (missing API keys)
    logger.error(f"Configuration error: {e}")
    raise
except PipecatBotError as e:
    # Bot initialization failures
    logger.error(f"Bot error: {e}")
    raise
```

### Function Call Error Handling

```python
async def handle_function(params):
    try:
        # Function logic
    except ValueError:
        await params.result_callback({
            "error": "InvalidInput",
            "message": "User-friendly error"
        })
    except Exception:
        await params.result_callback({
            "error": "SystemError",
            "message": "Please try again"
        })
```

### WebSocket Disconnection Handling

- Daily.co rooms auto-expire after 2 hours
- Bot handles WebSocket closure gracefully
- Frontend reconnection logic with exponential backoff

### Resource Cleanup

```python
# Best-effort cleanup pattern
if conversation.daily_room_id:
    try:
        await delete_room(conversation.daily_room_id)
    except Exception as e:
        # Log but don't fail - rooms auto-expire
        logger.error(f"Cleanup failed: {e}")
```

---

## Testing Strategy

### Unit Testing

#### Function Handlers
```python
# backend/tests/test_function_handlers.py
async def test_calculate_life_path():
    callback = MockCallback()
    params = FunctionCallParams(
        arguments={'birth_date': '1990-05-15'},
        result_callback=callback
    )
    await handle_calculate_life_path(params)
    assert callback.result['life_path_number'] == 7
```

#### Numerology Calculations
```python
# backend/tests/test_numerology_service.py
def test_life_path_calculation():
    result = calculate_life_path(date(1990, 5, 15))
    assert result == 7
```

### Integration Testing

#### Voice Pipeline
```python
# backend/tests/test_pipecat_integration.py
async def test_voice_pipeline():
    # Create test room
    room = await daily_service.create_room("test")

    # Spawn bot
    task = await run_bot(room['url'], room['token'], user)

    # Simulate conversation
    # Assert function calls
    # Verify context updates
```

### End-to-End Testing

1. **Manual Testing Protocol**:
   ```bash
   # Start backend
   make dev-backend

   # Create test conversation
   curl -X POST /api/v1/conversations/start

   # Join room in browser
   # Speak: "Tính con số đường đời của tôi"
   # Verify function execution
   # Check response generation
   ```

2. **Automated E2E**:
   - Mock Daily.co connection
   - Inject test audio streams
   - Verify complete flow

### Performance Testing

- Measure end-to-end latency (target: <1 second)
- Test concurrent conversations
- Monitor memory usage during long conversations
- Validate function call timeout handling

---

## Implementation Checklist

### Core Pipeline ✅
- [x] Pipecat pipeline setup
- [x] Daily.co transport configuration
- [x] Deepgram STT integration
- [x] Azure OpenAI LLM setup
- [x] ElevenLabs TTS integration
- [x] VAD implementation

### Function Calling ✅
- [x] FunctionSchema definitions
- [x] OpenAI format conversion
- [x] Async handler implementation
- [x] Function registration with LLM
- [x] Error handling in handlers

### Context Management ✅
- [x] LLM context aggregator
- [x] Function result integration
- [x] Conversation history tracking
- [x] System prompt management

### Language Support ✅
- [x] Vietnamese system prompt
- [x] Multi-language STT configuration
- [x] User context personalization

### API Endpoints ✅
- [x] /conversations/start
- [x] /conversations/{id}/end
- [x] Authentication integration
- [x] Error responses

### Frontend Integration 🚧
- [ ] Daily.co React Native setup
- [ ] Audio permission handling
- [ ] Voice visualization
- [ ] Conversation state management
- [ ] Error recovery UI

---

## Future Enhancements

1. **Advanced Features**:
   - Conversation resumption
   - Multi-turn context retention
   - Voice biometrics
   - Real-time translation

2. **Performance Optimizations**:
   - Audio codec optimization
   - Streaming function results
   - Predictive response caching
   - Edge deployment

3. **Monitoring & Analytics**:
   - Conversation metrics
   - Function call analytics
   - Latency tracking
   - User satisfaction scoring

4. **Security Enhancements**:
   - End-to-end encryption
   - PII redaction
   - Audit logging
   - Rate limiting per user

---

## References

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Daily.co API Reference](https://docs.daily.co/reference)
- [Deepgram API Guide](https://developers.deepgram.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [ElevenLabs API](https://docs.elevenlabs.io/)

---

*Last Updated: November 2024*
*Version: 1.0.0*