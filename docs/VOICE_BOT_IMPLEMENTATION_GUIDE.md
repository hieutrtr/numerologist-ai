# Voice Bot Implementation Guide
## Current State & Integration Patterns

### Quick Start

To test the voice bot locally:

```bash
# 1. Set up environment variables
cd backend
cp .env.example .env
# Add your API keys to .env

# 2. Start the backend
make dev-backend

# 3. Test voice conversation
curl -X POST http://localhost:8000/api/v1/conversations/start \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. Join the returned Daily.co URL in browser
```

---

## Critical Implementation Details

### 1. Context Aggregator Pattern (MUST FOLLOW)

**❌ INCORRECT** (causes infinite function loops):
```python
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantContextAggregator,
    LLMUserContextAggregator,
)

# DON'T DO THIS
user_aggregator = LLMUserContextAggregator()
assistant_aggregator = LLMAssistantContextAggregator()

pipeline = Pipeline([
    transport.input(),
    stt,
    user_aggregator,  # ❌ Won't track function results
    llm,
    tts,
    transport.output(),
    assistant_aggregator,  # ❌ Won't update context
])
```

**✅ CORRECT** (properly handles function results):
```python
# ALWAYS create aggregator from LLM service
context_aggregator = llm.create_context_aggregator(llm_context)

pipeline = Pipeline([
    transport.input(),
    stt,
    context_aggregator.user(),      # ✅ Tracks user messages
    llm,
    tts,
    transport.output(),
    context_aggregator.assistant(), # ✅ Updates with function results
])
```

### 2. Function Definition Pattern

**File**: `backend/src/voice_pipeline/numerology_functions.py`

```python
from pipecat.adapters.schemas.function_schema import FunctionSchema

# 1. Define using FunctionSchema
calculate_life_path_function = FunctionSchema(
    name="calculate_life_path",
    description="Calculate Life Path number...",
    properties={
        "birth_date": {
            "type": "string",
            "description": "YYYY-MM-DD format"
        }
    },
    required=["birth_date"]
)

# 2. Convert for OpenAILLMContext (REQUIRED)
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

# 3. Export in OpenAI format
numerology_tools = [
    _function_schema_to_openai_format(calculate_life_path_function),
    # ... other functions
]
```

### 3. Function Handler Pattern

**File**: `backend/src/voice_pipeline/function_handlers.py`

```python
from pipecat.services.llm_service import (
    FunctionCallParams,
    FunctionCallResultProperties
)

async def handle_calculate_life_path(params: FunctionCallParams):
    try:
        # Extract arguments
        birth_date = params.arguments.get("birth_date")

        # Perform calculation
        result = calculate_life_path(parsed_date)

        # CRITICAL: Set run_llm=True to continue conversation
        properties = FunctionCallResultProperties(run_llm=True)

        # Return via callback
        await params.result_callback(
            {"life_path_number": result},
            properties=properties  # ← MUST include this
        )
    except Exception as e:
        # Error handling
        await params.result_callback({
            "error": "CalculationError",
            "message": str(e)
        })
```

### 4. LLM Service Configuration

```python
# Initialize LLM with proper settings
llm = AzureLLMService(
    api_key=settings.azure_openai_api_key,
    endpoint=settings.azure_openai_endpoint,
    model=settings.azure_openai_model_deployment_name,
    api_version=settings.azure_openai_api_version,
    run_in_parallel=False,  # Sequential function execution
)

# Register ALL functions BEFORE creating context
llm.register_function("calculate_life_path", handle_calculate_life_path,
                     cancel_on_interruption=False)
llm.register_function("calculate_expression_number", handle_calculate_expression,
                     cancel_on_interruption=False)
# ... register other functions

# Create context with tools
llm_context = OpenAILLMContext(
    messages=[{"role": "system", "content": system_prompt}],
    tools=numerology_tools  # ← Must be OpenAI JSON format
)

# Create aggregator from LLM (CRITICAL)
context_aggregator = llm.create_context_aggregator(llm_context)
```

---

## Common Issues & Solutions

### Issue 1: Functions Called in Infinite Loop

**Symptom**: Same function called repeatedly
```log
Calling function: calculate_life_path
Calling function: calculate_life_path
Calling function: calculate_life_path
```

**Cause**: Context not updating with function results

**Solution**:
1. Use `llm.create_context_aggregator()`
2. Ensure `FunctionCallResultProperties(run_llm=True)`
3. Use aggregator methods in pipeline

### Issue 2: "Function not registered" Warning

**Symptom**:
```log
WARNING: Function 'calculate_life_path' not registered with LLM service
```

**Solution**:
```python
# Register BEFORE creating context
llm.register_function("calculate_life_path", handler)
# Then create context
llm_context = OpenAILLMContext(...)
```

### Issue 3: Serialization Error

**Symptom**:
```log
TypeError: Object of type FunctionSchema is not JSON serializable
```

**Solution**: Convert FunctionSchema to OpenAI format
```python
numerology_tools = [
    _function_schema_to_openai_format(func_schema)
    # NOT func_schema directly
]
```

### Issue 4: User Context Not Passed

**Symptom**: Generic greeting instead of personalized prompt

**Solution** in `conversations.py`:
```python
# Pass user to run_bot
asyncio.create_task(
    run_bot(room_url, meeting_token, current_user)  # ← Pass user
)
```

---

## Language-Specific Implementation

### Vietnamese Support

**System Prompt** (`backend/src/voice_pipeline/system_prompts.py`):
```python
def get_numerology_system_prompt(user: User) -> str:
    prompt = f"""
    Bạn là một nhà số học Pythagorean có kiến thức sâu rộng.

    THÔNG TIN NGƯỜI DÙNG:
    - Tên: {user.full_name}
    - Ngày Sinh: {formatted_date}

    CÔNG CỤ KHẢ DỤNG:
    - calculate_life_path: Tính con số đường đời
    - calculate_expression_number: Tính con số biểu đạt
    - calculate_soul_urge_number: Tính con số linh hồn
    - get_numerology_interpretation: Lấy giải thích chi tiết

    HƯỚNG DẪN:
    - Trả lời bằng tiếng Việt
    - Sử dụng công cụ khi cần tính toán
    - Giải thích ý nghĩa sau khi tính
    """
    return prompt
```

**Key Points**:
- System prompt in Vietnamese
- Function names remain in English
- Function descriptions in English (more reliable)

---

## Testing Checklist

### 1. Basic Conversation Test
```bash
# Start conversation
curl -X POST http://localhost:8000/api/v1/conversations/start \
  -H "Authorization: Bearer TOKEN"

# Join room and say:
"Hello"
# Expected: Greeting response

"Tính con số đường đời của tôi"
# Expected: Asks for birth date

"15 tháng 5 năm 1990"
# Expected: Calculates and explains Life Path 7
```

### 2. Function Calling Test
Monitor logs for:
```log
INFO: Calculating Life Path number for birth date: 1990-05-15
INFO: Successfully calculated Life Path number: 7
INFO: Function call result added to context
```

### 3. Context Retention Test
```
User: "Tính con số đường đời"
Bot: "Ngày sinh của bạn?"
User: "15/5/1990"
Bot: "Con số đường đời là 7..."
User: "Ý nghĩa của nó là gì?"
Bot: [Should explain 7 without recalculating]
```

---

## Debugging Tools

### 1. Enable Verbose Logging
```python
# In settings.py
PIPECAT_LOG_LEVEL = "DEBUG"

# In pipecat_bot.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Monitor Function Calls
```python
# Add to handlers
logger.info(f"Function called: {params.function_name}")
logger.info(f"Arguments: {params.arguments}")
logger.info(f"Result: {result}")
```

### 3. Track Context Updates
```python
# In pipeline
llm_context.get_messages()  # View current context
```

---

## Deployment Considerations

### Environment Variables
```env
# Production settings
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=gpt-4-prod
VOICE_LANGUAGE=vi  # or en
LOG_LEVEL=INFO

# Rate limiting
MAX_CONVERSATION_DURATION=1800  # 30 minutes
MAX_FUNCTIONS_PER_CONVERSATION=50
```

### Resource Management
```python
# Conversation cleanup
async def cleanup_stale_conversations():
    # Find conversations > 2 hours old
    # Delete Daily.co rooms
    # Mark as ended
```

### Monitoring
- Track function call frequency
- Monitor end-to-end latency
- Log error rates by type
- Track conversation duration

---

## Mobile Integration (React Native)

### Install Dependencies
```bash
cd mobile
npm install @daily-co/react-native-daily-js
npm install react-native-permissions
```

### Audio Permission Setup
```typescript
// iOS: Info.plist
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for voice conversations</string>

// Android: AndroidManifest.xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

### Conversation Hook
```typescript
export const useConversation = () => {
  const [call, setCall] = useState(null);

  const startConversation = async () => {
    // 1. Get room from API
    const { daily_room_url, daily_token } =
      await api.startConversation();

    // 2. Create Daily call
    const newCall = Daily.createCallObject();
    await newCall.join({ url: daily_room_url, token: daily_token });

    // 3. Handle events
    newCall.on('participant-joined', handleBotJoined);
    newCall.on('track-started', handleAudioStarted);

    setCall(newCall);
  };

  const endConversation = async () => {
    await call?.leave();
    await api.endConversation(conversationId);
  };

  return { startConversation, endConversation, isActive: !!call };
};
```

---

## Troubleshooting Guide

| Problem | Solution |
|---------|----------|
| Bot doesn't join room | Check Daily.co API key and room creation |
| No audio from bot | Verify ElevenLabs API key and voice_id |
| Bot doesn't understand Vietnamese | Check VOICE_LANGUAGE=vi in .env |
| Functions not working | Ensure all 4 functions registered with LLM |
| Context lost between messages | Verify using llm.create_context_aggregator() |
| High latency | Check network, consider edge deployment |

---

## Next Steps

1. **Immediate**:
   - Complete mobile UI implementation
   - Add conversation history persistence
   - Implement voice amplitude visualization

2. **Short-term**:
   - Add more numerology calculations
   - Implement conversation resumption
   - Add user preferences for voice

3. **Long-term**:
   - Multi-language support (Spanish, French)
   - Voice biometrics for authentication
   - Real-time translation feature

---

*Last Updated: November 2024*
*Implementation Status: Voice pipeline complete, mobile UI pending*