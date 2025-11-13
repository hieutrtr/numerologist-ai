# Voice Bot Boilerplate
## Production-Ready Pipecat Voice AI Template

This boilerplate provides a complete, battle-tested foundation for building voice AI applications using the Pipecat framework. It's extracted from a production numerology AI assistant and includes all essential patterns, error handling, and best practices.

## Features

✅ **Complete Voice Pipeline** - Pipecat orchestration with Daily.co WebRTC, Deepgram STT, Azure OpenAI LLM, ElevenLabs TTS
✅ **Function Calling System** - Properly implemented function calling with context aggregation
✅ **Multi-Language Support** - Template for English and Vietnamese (easily extendable)
✅ **Error Handling** - Comprehensive error boundaries and recovery
✅ **Production Patterns** - Lazy validation, best-effort cleanup, graceful degradation
✅ **Testing Infrastructure** - Unit and integration test templates
✅ **Mobile Ready** - React Native integration patterns

## Quick Start

### 1. Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 18+ (for mobile)
node --version
```

### 2. Backend Setup

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env with your API keys:
# - DEEPGRAM_API_KEY
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - ELEVENLABS_API_KEY
# - DAILY_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

### 3. Test Voice Bot

```bash
# Start conversation
curl -X POST http://localhost:8000/api/v1/conversations/start \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Join the returned Daily.co URL in browser
# Speak to test the voice pipeline
```

## Project Structure

```
boilerplate/
├── README.md                          # This file
├── IMPLEMENTATION_GUIDE.md            # Detailed implementation guide
├── backend/                           # FastAPI backend
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   ├── main.py                        # Application entry point
│   ├── core/
│   │   ├── settings.py                # Configuration management
│   │   ├── database.py                # Database setup
│   │   └── deps.py                    # Dependency injection
│   ├── voice_pipeline/
│   │   ├── pipecat_bot.py             # Main pipeline orchestration
│   │   ├── function_schemas.py        # Function definitions (TEMPLATE)
│   │   ├── function_handlers.py       # Function handlers (TEMPLATE)
│   │   └── system_prompts.py          # System prompt templates
│   ├── services/
│   │   └── daily_service.py           # Daily.co room management
│   ├── api/
│   │   └── endpoints/
│   │       └── conversations.py       # Conversation endpoints
│   └── tests/
│       ├── test_pipeline.py           # Pipeline tests
│       └── test_functions.py          # Function calling tests
├── mobile/                            # React Native mobile app
│   ├── README.md                      # Mobile setup guide
│   ├── package.json                   # Node dependencies
│   ├── App.tsx                        # App entry point
│   ├── app.json                       # Expo configuration
│   └── src/
│       ├── components/
│       │   ├── VoiceVisualizer.tsx    # Voice activity animation
│       │   └── ConnectionStatus.tsx   # Status indicator
│       ├── hooks/
│       │   └── useConversation.ts     # Conversation hook
│       ├── screens/
│       │   └── ConversationScreen.tsx # Main UI screen
│       └── services/
│           └── api.ts                 # Backend API client
└── docs/
    ├── ARCHITECTURE.md                # Architecture overview
    ├── FUNCTION_CALLING.md            # Function calling guide
    └── TROUBLESHOOTING.md             # Common issues & solutions
```

## Configuration

### Required API Keys

| Service | Purpose | Get From |
|---------|---------|----------|
| Deepgram | Speech-to-text | https://console.deepgram.com/ |
| Azure OpenAI | Language model | https://portal.azure.com/ |
| ElevenLabs | Text-to-speech | https://elevenlabs.io/ |
| Daily.co | WebRTC rooms | https://dashboard.daily.co/ |

### Environment Variables

```env
# Voice Services
DEEPGRAM_API_KEY=your_key
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=gpt-4
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Daily.co
DAILY_API_KEY=your_key

# Language
VOICE_LANGUAGE=en  # or vi, es, fr, de, ja, zh, pt

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# JWT
JWT_SECRET=your-secret-key
```

## Customization Guide

### 1. Add Your Own Functions

**Step 1**: Define function schema in `voice_pipeline/function_schemas.py`:

```python
from pipecat.adapters.schemas.function_schema import FunctionSchema

your_function = FunctionSchema(
    name="your_function_name",
    description="What this function does...",
    properties={
        "param1": {
            "type": "string",
            "description": "Parameter description"
        }
    },
    required=["param1"]
)
```

**Step 2**: Create handler in `voice_pipeline/function_handlers.py`:

```python
async def handle_your_function(params: FunctionCallParams):
    try:
        param1 = params.arguments.get("param1")

        # Your business logic here
        result = your_service.do_something(param1)

        # Return result
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback(
            {"result": result},
            properties=properties
        )
    except Exception as e:
        await params.result_callback({
            "error": "YourError",
            "message": str(e)
        })
```

**Step 3**: Register in `voice_pipeline/pipecat_bot.py`:

```python
llm.register_function("your_function_name", handle_your_function)
```

### 2. Customize System Prompt

Edit `voice_pipeline/system_prompts.py`:

```python
def get_system_prompt(user: Optional[User] = None) -> str:
    return f"""
    You are a helpful AI assistant specializing in [YOUR DOMAIN].

    AVAILABLE TOOLS:
    - your_function_name: Description of what it does

    GUIDELINES:
    - Be friendly and professional
    - Use tools when needed
    - Explain results clearly
    """
```

### 3. Change Language

Set `VOICE_LANGUAGE` in `.env`:

```env
VOICE_LANGUAGE=vi  # Vietnamese
```

Update system prompt in your language:

```python
if settings.voice_language == "vi":
    prompt = "Bạn là trợ lý AI thân thiện..."
elif settings.voice_language == "es":
    prompt = "Eres un asistente de IA útil..."
```

## Critical Implementation Patterns

### ✅ Context Aggregator (MUST USE THIS PATTERN)

```python
# CORRECT - Prevents infinite function loops
context_aggregator = llm.create_context_aggregator(llm_context)

pipeline = Pipeline([
    transport.input(),
    stt,
    context_aggregator.user(),      # ← From aggregator
    llm,
    tts,
    transport.output(),
    context_aggregator.assistant(), # ← From aggregator
])
```

### ✅ Function Handler Pattern

```python
async def handle_function(params: FunctionCallParams):
    # 1. Extract arguments
    arg = params.arguments.get("arg")

    # 2. Execute logic
    result = do_something(arg)

    # 3. Return with run_llm=True (CRITICAL)
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)
```

### ✅ Function Registration Flow

```python
# 1. Define schema
function_schema = FunctionSchema(...)

# 2. Convert to OpenAI format
function_json = _function_schema_to_openai_format(function_schema)

# 3. Register handler
llm.register_function("function_name", handler)

# 4. Add to context
llm_context = OpenAILLMContext(
    messages=[...],
    tools=[function_json]  # ← OpenAI format
)

# 5. Create aggregator
context_aggregator = llm.create_context_aggregator(llm_context)
```

## Testing

### Unit Tests

```bash
pytest tests/test_functions.py -v
```

### Integration Tests

```bash
pytest tests/test_pipeline.py -v
```

### Manual E2E Test

```bash
# Run backend
uvicorn main:app --reload

# In another terminal
python scripts/test_voice_conversation.py
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Infinite function loops | Use `llm.create_context_aggregator()` |
| Functions not registered | Register before creating context |
| Serialization errors | Convert FunctionSchema to OpenAI JSON |
| No audio from bot | Check ElevenLabs API key and voice_id |

See `docs/TROUBLESHOOTING.md` for detailed solutions.

## Deployment

### Backend (Azure/AWS)

```bash
# Build Docker image
docker build -t voicebot-api .

# Run container
docker run -p 8000:8000 --env-file .env voicebot-api
```

### Database Migration

```bash
alembic upgrade head
```

### Environment Variables

Set all required API keys in your hosting platform's environment configuration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Device                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Daily.co WebRTC Client                 │   │
│  │  - Microphone Input                                 │   │
│  │  - Speaker Output                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ WebRTC (Audio Stream)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Pipecat Voice Pipeline                    │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Daily   │→ │ Deepgram │→ │  Azure   │→ │ElevenLabs│  │
│  │Transport │  │   STT    │  │  OpenAI  │  │   TTS    │  │
│  └──────────┘  └──────────┘  └────┬─────┘  └──────────┘  │
│                                    │                        │
│                                    ↓                        │
│                            ┌───────────────┐               │
│                            │   Function    │               │
│                            │   Handlers    │               │
│                            └───────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Contributing

This boilerplate is designed to be copied and customized for your use case. Feel free to:

1. Remove features you don't need
2. Add your domain-specific logic
3. Extend with additional services
4. Adapt the system prompts

## License

MIT License - Use freely in your projects

## Support & Resources

- **Documentation**: See `docs/` folder
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

## Credits

Extracted from the Numerologist AI project, battle-tested in production with Vietnamese language support and complex function calling logic.

---

**Ready to build your voice AI?** Start with `backend/main.py` and customize from there!