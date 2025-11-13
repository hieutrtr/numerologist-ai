# Voice Bot Implementation Guide
## Step-by-Step Setup and Customization

This guide walks you through customizing the boilerplate for your specific use case.

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Define Your Functions](#define-your-functions)
3. [Implement Function Handlers](#implement-function-handlers)
4. [Customize System Prompt](#customize-system-prompt)
5. [Test Your Bot](#test-your-bot)
6. [Deploy to Production](#deploy-to-production)

---

## Initial Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required Services
DEEPGRAM_API_KEY=your_deepgram_key
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
ELEVENLABS_API_KEY=your_elevenlabs_key
DAILY_API_KEY=your_daily_key

# Optional: Change language
VOICE_LANGUAGE=en  # or vi, es, fr, etc.
```

### 3. Test Configuration

```bash
python -c "from core.settings import settings; print('Config OK')"
```

---

## Define Your Functions

### Step 1: Identify Your Use Case

What will your voice bot do? Examples:
- **Customer Support**: Query order status, update shipping addresses
- **Health Assistant**: Log symptoms, retrieve medical info
- **Smart Home**: Control devices, check status
- **Education**: Answer questions, provide exercises

### Step 2: List Required Functions

For each capability, define a function:

| Capability | Function Name | Parameters |
|------------|---------------|------------|
| Query orders | `get_order_status` | `order_id: string` |
| Update address | `update_shipping_address` | `order_id: string, address: string` |

### Step 3: Define Function Schemas

Edit `backend/voice_pipeline/function_schemas.py`:

```python
from pipecat.adapters.schemas.function_schema import FunctionSchema

# Example: Order status lookup
get_order_status_function = FunctionSchema(
    name="get_order_status",
    description=(
        "Look up the current status of a customer order. "
        "Use this when the user asks about their order, "
        "delivery status, or tracking information."
    ),
    properties={
        "order_id": {
            "type": "string",
            "description": (
                "The unique order identifier (e.g., 'ORD-12345'). "
                "If the user doesn't provide it, ask them for their order number."
            )
        }
    },
    required=["order_id"]
)

# Add to function_tools list at bottom of file
function_tools = [
    _function_schema_to_openai_format(get_order_status_function),
    # ... other functions
]
```

### Function Schema Best Practices

✅ **DO:**
- Use clear, verb-based names (`get_`, `set_`, `update_`)
- Write detailed descriptions (helps LLM decide when to call)
- Document parameter formats and expectations
- Specify what triggers the function

❌ **DON'T:**
- Use vague names (`process`, `handle`, `do_thing`)
- Skip parameter descriptions
- Make assumptions about user input format

---

## Implement Function Handlers

### Step 1: Create Handler

Edit `backend/voice_pipeline/function_handlers.py`:

```python
async def handle_get_order_status(params: FunctionCallParams):
    """
    Handle order status lookup.

    Args:
        params: Contains arguments and result callback

    Returns:
        Via callback: Order status details or error
    """
    try:
        # 1. Extract arguments
        order_id = params.arguments.get("order_id")
        logger.info(f"Looking up order: {order_id}")

        # 2. Validate input
        if not order_id or not order_id.startswith("ORD-"):
            await params.result_callback({
                "error": "InvalidOrderId",
                "message": "Please provide a valid order number starting with ORD-"
            })
            return

        # 3. Execute business logic
        # TODO: Replace with your actual implementation
        order_status = await fetch_order_from_database(order_id)

        # 4. Return result with run_llm=True
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback({
            "order_id": order_id,
            "status": order_status["status"],
            "estimated_delivery": order_status["delivery_date"],
            "tracking_number": order_status["tracking"]
        }, properties=properties)

    except OrderNotFoundError:
        await params.result_callback({
            "error": "OrderNotFound",
            "message": f"No order found with ID {order_id}"
        })

    except Exception as e:
        logger.error(f"Error fetching order: {e}", exc_info=True)
        await params.result_callback({
            "error": "SystemError",
            "message": "Unable to retrieve order status. Please try again."
        })
```

### Step 2: Register Handler

Edit `backend/voice_pipeline/pipecat_bot.py`:

Find the function registration section and add:

```python
# Import your handler
from voice_pipeline.function_handlers import handle_get_order_status

# In run_bot() function, after creating llm service:
llm.register_function(
    "get_order_status",
    handle_get_order_status,
    cancel_on_interruption=False
)
```

### Handler Implementation Checklist

- [ ] Extract all required arguments
- [ ] Validate inputs (type, format, required fields)
- [ ] Add logging (info level for calls, error for failures)
- [ ] Implement business logic (API calls, database queries)
- [ ] Create `FunctionCallResultProperties(run_llm=True)` ← **CRITICAL!**
- [ ] Call `params.result_callback(result, properties=properties)`
- [ ] Catch all exceptions
- [ ] Return user-friendly error messages
- [ ] Test handler independently

---

## Customize System Prompt

### Step 1: Define Your Bot's Personality

Edit `backend/voice_pipeline/pipecat_bot.py` → `_get_system_prompt()`:

```python
def _get_system_prompt(user_data: Optional[dict] = None) -> str:
    """Customize this for your use case!"""

    # Example: Customer support bot
    prompt = """
    You are a friendly customer support assistant for TechCorp.

    YOUR ROLE:
    - Help customers track orders
    - Update shipping information
    - Answer product questions
    - Escalate complex issues to human agents

    AVAILABLE TOOLS:
    - get_order_status: Look up order tracking and status
    - update_shipping_address: Modify delivery address
    - search_products: Find products by name or category

    GUIDELINES:
    - Always greet customers warmly
    - Ask for order numbers when needed
    - Confirm changes before executing
    - Keep responses concise (this is voice, not text)
    - Use casual, friendly language
    - If you can't help, offer to transfer to a human agent

    EXAMPLE INTERACTIONS:
    User: "Where's my order?"
    You: "I can help you track your order! Could you provide your order number? It starts with ORD-"

    User: "ORD-12345"
    You: [Call get_order_status] "Your order is currently in transit and should arrive on Friday!"
    """

    # Add personalization if available
    if user_data:
        customer_name = user_data.get("name")
        if customer_name:
            prompt += f"\\n\\nYou are currently helping {customer_name}."

    return prompt
```

### Prompt Engineering Tips

✅ **DO:**
- Clearly state the bot's role and capabilities
- List available tools with descriptions
- Provide example interactions
- Set tone and personality guidelines
- Specify what to do when stuck

❌ **DON'T:**
- Make the prompt too long (keep < 1000 words)
- Use technical jargon users won't understand
- Promise capabilities you haven't implemented
- Forget to mention voice format (concise responses)

### Multi-Language Support

```python
def _get_system_prompt(user_data: Optional[dict] = None) -> str:
    if settings.voice_language == "vi":
        return """
        Bạn là trợ lý hỗ trợ khách hàng thân thiện của TechCorp.

        VAI TRÒ CỦA BẠN:
        - Giúp khách hàng theo dõi đơn hàng
        - Cập nhật thông tin giao hàng
        ...
        """
    elif settings.voice_language == "es":
        return """
        Eres un asistente de servicio al cliente amigable de TechCorp.
        ...
        """
    else:  # Default to English
        return """
        You are a friendly customer support assistant...
        """
```

---

## Test Your Bot

### 1. Unit Test Functions

Create `backend/tests/test_my_functions.py`:

```python
import pytest
from voice_pipeline.function_handlers import handle_get_order_status
from pipecat.services.llm_service import FunctionCallParams

class MockCallback:
    def __init__(self):
        self.result = None

    async def __call__(self, result, properties=None):
        self.result = result

@pytest.mark.asyncio
async def test_get_order_status_success():
    callback = MockCallback()
    params = FunctionCallParams(
        function_name='get_order_status',
        arguments={'order_id': 'ORD-12345'},
        result_callback=callback,
        llm_context=None,
        tool_call_id='test-123'
    )

    await handle_get_order_status(params)

    assert callback.result is not None
    assert 'order_id' in callback.result
    assert callback.result['order_id'] == 'ORD-12345'

@pytest.mark.asyncio
async def test_get_order_status_invalid_id():
    callback = MockCallback()
    params = FunctionCallParams(
        function_name='get_order_status',
        arguments={'order_id': 'INVALID'},
        result_callback=callback,
        llm_context=None,
        tool_call_id='test-123'
    )

    await handle_get_order_status(params)

    assert 'error' in callback.result
    assert callback.result['error'] == 'InvalidOrderId'
```

Run tests:

```bash
pytest backend/tests/test_my_functions.py -v
```

### 2. Manual Voice Test

```bash
# Start backend
cd backend
uvicorn main:app --reload
```

In another terminal:

```bash
# Create test conversation
curl -X POST http://localhost:8000/api/v1/conversations/start \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"

# Copy the returned daily_room_url and open in browser
# Allow microphone access and speak
```

### 3. Test Checklist

- [ ] Bot responds to greetings
- [ ] Functions are called when appropriate
- [ ] Function results are spoken back naturally
- [ ] Errors are handled gracefully
- [ ] Conversation flows naturally
- [ ] No infinite loops
- [ ] Context is maintained between turns

---

## Deploy to Production

### 1. Environment Setup

Create production `.env`:

```env
# Change all these for production!
DEBUG=false
ENVIRONMENT=production
JWT_SECRET=<generate-new-secure-secret>

# Production database
DATABASE_URL=postgresql://user:pass@prod-host:5432/db

# Keep API keys secure (use secret manager)
DEEPGRAM_API_KEY=<from-secret-manager>
AZURE_OPENAI_API_KEY=<from-secret-manager>
ELEVENLABS_API_KEY=<from-secret-manager>
DAILY_API_KEY=<from-secret-manager>

# Restrict CORS
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Production logging
LOG_LEVEL=INFO
```

### 2. Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t voicebot-api .
docker run -p 8000:8000 --env-file .env voicebot-api
```

### 3. Monitoring

Add health check endpoint in `backend/main.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }
```

Monitor:
- Function call frequency
- Error rates
- Response latency
- Conversation duration

### 4. Security Checklist

- [ ] Changed JWT_SECRET
- [ ] API keys in environment variables (not code)
- [ ] CORS restricted to your domains
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Database credentials secured
- [ ] Logs don't contain sensitive data

---

## Troubleshooting

### Issue: Functions Called in Infinite Loop

**Symptom**: Same function called repeatedly

**Cause**: Not using `llm.create_context_aggregator()`

**Solution**:
```python
# In pipecat_bot.py
context_aggregator = llm.create_context_aggregator(llm_context)

pipeline = Pipeline([
    ...
    context_aggregator.user(),
    llm,
    ...
    context_aggregator.assistant(),
])
```

### Issue: "Function Not Registered" Warning

**Symptom**: Warning in logs about unregistered function

**Solution**: Register BEFORE creating context
```python
llm.register_function("function_name", handler)
# THEN create context
llm_context = OpenAILLMContext(...)
```

### Issue: Bot Doesn't Respond

**Check**:
1. API keys configured correctly
2. Daily.co room created successfully
3. Pipeline started without errors
4. Check logs for exceptions

### Issue: Poor Voice Quality

**Try**:
1. Different ElevenLabs voice_id
2. Adjust VAD_SILENCE_TIMEOUT_MS
3. Check network latency
4. Use higher quality audio codec

---

## Next Steps

1. **Add More Functions**: Expand capabilities
2. **Improve Prompts**: Refine based on user feedback
3. **Add Persistence**: Store conversation history
4. **Multi-User Support**: User authentication
5. **Analytics**: Track usage and performance

## Resources

- **Pipecat Docs**: https://docs.pipecat.ai/
- **Daily.co API**: https://docs.daily.co/
- **Deepgram API**: https://developers.deepgram.com/
- **Azure OpenAI**: https://learn.microsoft.com/azure/ai-services/openai/

---

**Need Help?** Check the troubleshooting docs or review the original implementation in the parent project.