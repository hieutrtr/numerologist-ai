"""
Function Calling Definitions - TEMPLATE

Define your custom functions here using Pipecat's FunctionSchema format.
These functions will be available to the LLM during voice conversations.

Example Use Cases:
- Query databases
- Call external APIs
- Perform calculations
- Retrieve user-specific data
- Execute business logic

Pattern:
1. Define function with FunctionSchema
2. Convert to OpenAI JSON format
3. Export in function_tools list
"""

from pipecat.adapters.schemas.function_schema import FunctionSchema


# =============================================================================
# EXAMPLE FUNCTION: Get Weather
# =============================================================================
# TODO: Replace this with your own function definitions

get_weather_function = FunctionSchema(
    name="get_weather",
    description=(
        "Get the current weather for a specified location. "
        "Use this when the user asks about weather conditions, "
        "temperature, or forecast."
    ),
    properties={
        "location": {
            "type": "string",
            "description": (
                "City name or location (e.g., 'San Francisco', 'London', 'Tokyo'). "
                "If user doesn't specify, ask for clarification."
            )
        },
        "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Temperature unit preference. Defaults to celsius."
        }
    },
    required=["location"]
)


# =============================================================================
# EXAMPLE FUNCTION: Set Reminder
# =============================================================================
# TODO: Add more functions as needed

set_reminder_function = FunctionSchema(
    name="set_reminder",
    description=(
        "Create a reminder for the user. "
        "Use this when the user wants to remember something or "
        "schedule a notification."
    ),
    properties={
        "message": {
            "type": "string",
            "description": "The reminder message content"
        },
        "time": {
            "type": "string",
            "description": (
                "When to trigger the reminder. "
                "Format: ISO 8601 datetime or relative time "
                "(e.g., '2025-01-15T14:30:00', 'in 2 hours', 'tomorrow at 9am')"
            )
        }
    },
    required=["message", "time"]
)


# =============================================================================
# CONVERSION TO OPENAI FORMAT (REQUIRED)
# =============================================================================

def _function_schema_to_openai_format(func_schema: FunctionSchema) -> dict:
    """
    Convert Pipecat FunctionSchema to OpenAI JSON format.

    This is required because OpenAILLMContext expects JSON, not FunctionSchema objects.

    Args:
        func_schema: Pipecat FunctionSchema

    Returns:
        OpenAI-compatible function definition
    """
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


# =============================================================================
# EXPORT FUNCTIONS (Add your functions to this list)
# =============================================================================

function_tools = [
    _function_schema_to_openai_format(get_weather_function),
    _function_schema_to_openai_format(set_reminder_function),
    # TODO: Add your converted functions here
]


# =============================================================================
# USAGE NOTES
# =============================================================================

"""
To add a new function:

1. Define the schema:
   ```python
   my_function = FunctionSchema(
       name="my_function_name",
       description="What it does...",
       properties={
           "param1": {
               "type": "string",
               "description": "Parameter description"
           }
       },
       required=["param1"]
   )
   ```

2. Add to function_tools list:
   ```python
   function_tools = [
       _function_schema_to_openai_format(my_function),
       # ... other functions
   ]
   ```

3. Create handler in function_handlers.py

4. Register in pipecat_bot.py:
   ```python
   llm.register_function("my_function_name", handle_my_function)
   ```

Best Practices:
- Use clear, descriptive function names
- Provide detailed descriptions (helps LLM decide when to call)
- Specify parameter types and descriptions
- Mark required vs optional parameters
- Keep function purposes focused (single responsibility)
- Document expected parameter formats
"""
