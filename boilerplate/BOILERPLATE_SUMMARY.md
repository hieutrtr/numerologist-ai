# Voice Bot Boilerplate - Summary

## Overview

This boilerplate provides a production-ready foundation for building voice AI applications using the Pipecat framework. It's extracted from a real production numerology AI assistant and includes all battle-tested patterns, proper error handling, and best practices discovered through debugging real issues.

## What's Included

### 📚 Documentation (3 guides)

1. **README.md** - Complete overview
   - Features and architecture
   - Quick start instructions
   - Project structure explanation
   - Configuration guide
   - Customization examples
   - Critical implementation patterns

2. **QUICKSTART.md** - 10-minute setup
   - Step-by-step installation
   - API key acquisition guide
   - Configuration walkthrough
   - Verification tests
   - Troubleshooting tips

3. **IMPLEMENTATION_GUIDE.md** - Deep dive
   - Function definition tutorial
   - Handler implementation patterns
   - System prompt customization
   - Testing strategies
   - Deployment checklist
   - Common issues and solutions

### 🏗️ Backend Structure (Complete FastAPI App)

```
backend/
├── main.py                    # Application entry point
├── requirements.txt           # All dependencies
├── .env.example              # Configuration template
├── core/
│   └── settings.py           # Centralized config
├── voice_pipeline/
│   ├── pipecat_bot.py        # Main pipeline (400+ lines)
│   ├── function_schemas.py   # Function definitions
│   └── function_handlers.py  # Handler implementations
├── services/
│   └── daily_service.py      # Daily.co integration
├── api/
│   └── endpoints/
│       └── conversations.py  # API endpoints
└── tests/
    └── __init__.py          # Test structure
```

### ✨ Key Features

#### 1. Complete Voice Pipeline
- Daily.co WebRTC transport with VAD
- Deepgram multi-language STT
- Azure OpenAI LLM integration
- ElevenLabs TTS synthesis
- Proper component ordering

#### 2. Function Calling System
- **FunctionSchema** pattern (Pipecat standard)
- **OpenAI format conversion** (for context compatibility)
- **Async handler pattern** with callbacks
- **FunctionCallResultProperties** (prevents infinite loops)
- Two example functions (get_weather, set_reminder)

#### 3. Context Aggregation (Critical!)
```python
# The pattern that prevents infinite loops
context_aggregator = llm.create_context_aggregator(llm_context)

pipeline = Pipeline([
    ...
    context_aggregator.user(),      # ← Captures user messages
    llm,                            # ← Processes with full context
    ...
    context_aggregator.assistant(), # ← Updates with function results
])
```

#### 4. Multi-Language Support
- Configurable via `VOICE_LANGUAGE` env var
- Supports: en, vi, es, fr, de, ja, zh, pt
- Language-specific STT models
- System prompt templates for each language

#### 5. Error Handling
- Comprehensive try-catch blocks
- User-friendly error messages
- Best-effort cleanup (graceful degradation)
- Detailed logging throughout

#### 6. Production Patterns
- Lazy validation (fails at runtime, not import)
- Environment-based configuration
- Health check endpoints
- CORS configuration
- Structured logging

### 🎯 Template Functions

#### Example 1: Get Weather
```python
# In function_schemas.py
get_weather_function = FunctionSchema(
    name="get_weather",
    description="Get current weather...",
    properties={"location": {...}, "unit": {...}},
    required=["location"]
)

# In function_handlers.py
async def handle_get_weather(params: FunctionCallParams):
    location = params.arguments.get("location")
    # Business logic here
    properties = FunctionCallResultProperties(run_llm=True)
    await params.result_callback(result, properties=properties)
```

#### Example 2: Set Reminder
Similar pattern for reminder creation, showing validation and error handling.

### 📋 Configuration

#### Required API Keys
- **Deepgram**: Speech-to-text (nova-3-general model)
- **Azure OpenAI**: Language model (GPT-4 recommended)
- **ElevenLabs**: Text-to-speech (Rachel voice default)
- **Daily.co**: WebRTC room management

#### Environment Variables
Complete `.env.example` with:
- All required service keys
- Optional configurations
- Development defaults
- Production security notes
- Detailed comments for each setting

### 🔧 Customization Points

#### 1. Define Your Functions
Edit `voice_pipeline/function_schemas.py` to add your business logic functions.

#### 2. Implement Handlers
Edit `voice_pipeline/function_handlers.py` with your actual implementations.

#### 3. Customize System Prompt
Edit `voice_pipeline/pipecat_bot.py` → `_get_system_prompt()` to define your bot's personality.

#### 4. Add Authentication
Edit `api/endpoints/conversations.py` to add user authentication.

#### 5. Configure Language
Set `VOICE_LANGUAGE` in `.env` to change conversation language.

### 🧪 Testing Support

#### Unit Test Template
```python
@pytest.mark.asyncio
async def test_function_handler():
    callback = MockCallback()
    params = FunctionCallParams(...)
    await handle_your_function(params)
    assert callback.result['expected_key'] == 'expected_value'
```

#### Integration Test Pattern
- Mock Daily.co connections
- Inject test audio streams
- Verify complete flow

### 🚀 Deployment Ready

#### Docker Support
- Dockerfile template included
- Environment variable injection
- Health check configuration

#### Production Checklist
- [ ] Change JWT_SECRET
- [ ] Secure API keys
- [ ] Restrict CORS
- [ ] Enable HTTPS
- [ ] Configure rate limiting
- [ ] Set up monitoring

### 📊 Patterns Extracted from Production

#### Critical Pattern: Context Aggregation
The most important lesson learned - using `llm.create_context_aggregator()` instead of separate aggregators prevents infinite function calling loops by ensuring function results are properly added to conversation context.

#### Best-Effort Cleanup
Daily.co rooms auto-expire, so deletion failures don't break the application. Log and continue.

#### Lazy Validation
Settings are loaded at import time but validated at function call time, allowing tests to mock without import failures.

#### Sequential Function Calling
`run_in_parallel=False` ensures functions execute in order when multiple are needed.

## Usage Scenarios

### Scenario 1: Customer Support Bot
Replace example functions with:
- `get_order_status(order_id)`
- `update_shipping_address(order_id, address)`
- `search_products(query)`

### Scenario 2: Health Assistant
Replace with:
- `log_symptoms(symptoms, severity)`
- `get_medication_info(medication_name)`
- `schedule_appointment(date, time, doctor)`

### Scenario 3: Smart Home Control
Replace with:
- `control_device(device_id, action)`
- `get_device_status(device_id)`
- `create_automation(trigger, action)`

## File Sizes

- **Total**: ~2,750 lines of code and documentation
- **pipecat_bot.py**: ~400 lines (fully documented)
- **function_handlers.py**: ~300 lines (with examples and notes)
- **function_schemas.py**: ~250 lines (with templates)
- **IMPLEMENTATION_GUIDE.md**: ~600 lines
- **README.md**: ~450 lines
- **QUICKSTART.md**: ~250 lines

## What Makes This Different

### vs Starting from Scratch
- Saves 40+ hours of implementation and debugging
- Includes patterns that prevent common pitfalls
- Battle-tested error handling
- Production-ready structure

### vs Official Pipecat Examples
- Complete FastAPI integration
- Function calling fully implemented
- Multi-language support included
- Real-world patterns (not just demos)
- Comprehensive documentation

### vs Generic Templates
- Based on actual production code
- Includes lessons from debugging real issues
- Vietnamese language support (demonstrates i18n)
- Complete function calling example with handlers

## Quick Stats

- **Setup Time**: 10 minutes (with QUICKSTART.md)
- **Lines of Code**: 2,750+
- **Documentation**: 1,300+ lines
- **Example Functions**: 2 complete examples
- **Supported Languages**: 8 (en, vi, es, fr, de, ja, zh, pt)
- **API Services**: 4 (Deepgram, Azure OpenAI, ElevenLabs, Daily.co)
- **License**: MIT (use freely)

## Success Path

1. **Read QUICKSTART.md** → Get running in 10 minutes
2. **Read IMPLEMENTATION_GUIDE.md** → Understand customization
3. **Define your functions** → `function_schemas.py`
4. **Implement handlers** → `function_handlers.py`
5. **Customize prompt** → `pipecat_bot.py`
6. **Test locally** → `uvicorn main:app --reload`
7. **Deploy** → Docker or cloud platform

## Support

- **Documentation**: See docs/ folder in boilerplate
- **Examples**: Two complete function examples included
- **Patterns**: All critical patterns documented inline
- **Reference**: Parent project has full production implementation

## Credits

Extracted from **Numerologist AI** - A production voice bot with:
- 4 complex numerology calculation functions
- Vietnamese language support with cultural context
- Database integration for interpretations
- Real user conversations in production

---

**Ready to build?** Start with `QUICKSTART.md` and you'll have a working voice bot in 10 minutes!

*Last Updated: November 2024*