"""
Function Call Handlers - TEMPLATE

Implement async handlers for each function defined in function_schemas.py.
These handlers execute when the LLM calls functions during voice conversations.

Handler Pattern:
1. Extract arguments from params.arguments
2. Execute business logic
3. Return results via params.result_callback()
4. CRITICAL: Set FunctionCallResultProperties(run_llm=True)

Error Handling:
- Catch exceptions gracefully
- Return user-friendly error messages
- Never let handlers crash the bot
"""

import logging
from pipecat.services.llm_service import FunctionCallParams, FunctionCallResultProperties

# Configure logger
logger = logging.getLogger(__name__)


# =============================================================================
# EXAMPLE HANDLER: Get Weather
# =============================================================================
# TODO: Replace with your actual implementation

async def handle_get_weather(params: FunctionCallParams):
    """
    Handle weather lookup function call.

    Args:
        params: FunctionCallParams containing:
            - arguments: {"location": str, "unit": str (optional)}
            - result_callback: Async function to return results

    Returns:
        Via callback: {"temperature": float, "condition": str, "location": str}
                     or {"error": str, "message": str}

    Example:
        LLM calls with {"location": "San Francisco", "unit": "celsius"}
        → Returns {"temperature": 18, "condition": "Sunny", "location": "San Francisco"}
    """
    try:
        # 1. Extract arguments
        location = params.arguments.get("location")
        unit = params.arguments.get("unit", "celsius")

        logger.info(f"Getting weather for {location} in {unit}")

        # 2. Execute business logic
        # TODO: Replace with actual weather API call
        result = {
            "temperature": 18 if unit == "celsius" else 64,
            "condition": "Sunny",
            "location": location,
            "unit": unit
        }

        logger.info(f"Weather retrieved: {result}")

        # 3. Return result via callback
        # CRITICAL: Set run_llm=True to continue conversation
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback(result, properties=properties)

    except KeyError as e:
        logger.error(f"Missing required parameter: {e}")
        await params.result_callback({
            "error": "MissingParameter",
            "message": f"Required parameter missing: {e}"
        })

    except Exception as e:
        logger.error(f"Error in handle_get_weather: {e}", exc_info=True)
        await params.result_callback({
            "error": "WeatherError",
            "message": "Unable to fetch weather. Please try again."
        })


# =============================================================================
# EXAMPLE HANDLER: Set Reminder
# =============================================================================
# TODO: Implement your handler logic

async def handle_set_reminder(params: FunctionCallParams):
    """
    Handle reminder creation function call.

    Args:
        params: FunctionCallParams containing:
            - arguments: {"message": str, "time": str}
            - result_callback: Async function to return results

    Returns:
        Via callback: {"reminder_id": str, "scheduled_time": str}
                     or {"error": str, "message": str}
    """
    try:
        # 1. Extract arguments
        message = params.arguments.get("message")
        time = params.arguments.get("time")

        logger.info(f"Creating reminder: '{message}' at {time}")

        # 2. Validate inputs
        if not message or not message.strip():
            await params.result_callback({
                "error": "InvalidInput",
                "message": "Reminder message cannot be empty"
            })
            return

        # 3. Execute business logic
        # TODO: Replace with actual reminder storage
        result = {
            "reminder_id": "rem_12345",
            "message": message,
            "scheduled_time": time,
            "status": "created"
        }

        logger.info(f"Reminder created: {result}")

        # 4. Return result
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback(result, properties=properties)

    except Exception as e:
        logger.error(f"Error in handle_set_reminder: {e}", exc_info=True)
        await params.result_callback({
            "error": "ReminderError",
            "message": "Unable to create reminder. Please try again."
        })


# =============================================================================
# ADD YOUR HANDLERS BELOW
# =============================================================================

# TODO: Implement your custom function handlers
# Follow the pattern above:
# 1. Extract arguments
# 2. Validate inputs
# 3. Execute business logic
# 4. Return via callback with run_llm=True
# 5. Handle errors gracefully


# =============================================================================
# USAGE NOTES
# =============================================================================

"""
Handler Implementation Checklist:

✅ Extract all required arguments from params.arguments
✅ Validate inputs (check for None, empty strings, invalid formats)
✅ Add logging for debugging (info for success, error for failures)
✅ Execute business logic (API calls, database queries, calculations)
✅ Create FunctionCallResultProperties(run_llm=True)  ← CRITICAL!
✅ Call params.result_callback(result, properties=properties)
✅ Catch and handle all exceptions
✅ Return user-friendly error messages

Common Mistakes to Avoid:

❌ Forgetting to set run_llm=True (causes infinite loops or no response)
❌ Not handling exceptions (crashes the bot)
❌ Not validating inputs (causes downstream errors)
❌ Returning raw exception messages (exposes implementation details)
❌ Blocking operations without async/await (blocks the pipeline)

Best Practices:

✅ Use async/await for all I/O operations
✅ Log function calls for debugging and monitoring
✅ Return structured data (dicts with consistent keys)
✅ Provide context in error messages
✅ Keep handlers focused (single responsibility)
✅ Test handlers independently before integration

Testing:

```python
# Create mock callback
class MockCallback:
    def __init__(self):
        self.result = None

    async def __call__(self, result, properties=None):
        self.result = result

# Test handler
callback = MockCallback()
params = FunctionCallParams(
    function_name='get_weather',
    arguments={'location': 'Tokyo'},
    result_callback=callback
)
await handle_get_weather(params)
assert callback.result['location'] == 'Tokyo'
```

Registration in pipecat_bot.py:

```python
llm.register_function("get_weather", handle_get_weather,
                     cancel_on_interruption=False)
llm.register_function("set_reminder", handle_set_reminder,
                     cancel_on_interruption=False)
```
"""
