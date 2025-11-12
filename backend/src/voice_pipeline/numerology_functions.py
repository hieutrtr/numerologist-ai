"""
Numerology Function Calling Definitions for Pipecat Integration

This module provides Pipecat-formatted function calling definitions (tools) that enable
the AI to invoke numerology calculations and retrieve interpretations during voice
conversations. These tool definitions follow Pipecat's FunctionSchema format.

The tools defined here bridge the gap between conversational AI and the numerology engine,
enabling the AI to:
1. Calculate numerology numbers from user-provided data (birth date, name)
2. Retrieve expert interpretations from the knowledge base
3. Provide personalized numerology guidance in natural conversation

Integration with Pipecat:
-----------------------
These tools are designed to work with Pipecat's LLM services and context management:

```python
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from src.voice_pipeline.numerology_functions import numerology_tools

# Create LLM context with tools
llm_context = OpenAILLMContext(
    messages=[{"role": "system", "content": system_prompt}],
    tools=numerology_tools
)

# Register function handlers with LLM service
from src.voice_pipeline.function_handlers import (
    handle_calculate_life_path,
    handle_calculate_expression,
    handle_calculate_soul_urge,
    handle_get_interpretation
)

llm.register_function("calculate_life_path", handle_calculate_life_path)
llm.register_function("calculate_expression_number", handle_calculate_expression)
llm.register_function("calculate_soul_urge_number", handle_calculate_soul_urge)
llm.register_function("get_numerology_interpretation", handle_get_interpretation)
```

References:
-----------
- Pipecat Function Calling: https://docs.pipecat.ai/guides/learn/function-calling
- Story 4.1: numerology_service.py - Calculation implementations
- Story 4.2: NumerologyInterpretation model - Database schema
- Story 4.4: function_handlers.py - Handler implementations
"""

from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

# Define function schemas using Pipecat's FunctionSchema
calculate_life_path_function = FunctionSchema(
    name="calculate_life_path",
    description=(
        "Calculate the user's Life Path number from their birth date. "
        "The Life Path number reveals their life purpose, natural tendencies, "
        "and the journey they're meant to take in this lifetime. "
        "Use this when the user asks about their life path, purpose, destiny, "
        "or provides their birth date. "
        "Returns a number between 1-9 or master numbers 11, 22, 33."
    ),
    properties={
        "birth_date": {
            "type": "string",
            "description": (
                "User's birth date in YYYY-MM-DD format (e.g., 1990-05-15). "
                "Ask the user for their complete birth date including year, "
                "month, and day if not provided."
            )
        }
    },
    required=["birth_date"]
)

calculate_expression_number_function = FunctionSchema(
    name="calculate_expression_number",
    description=(
        "Calculate the user's Expression number from their full birth name. "
        "The Expression number reveals their natural talents, abilities, "
        "and the potential they were born with. It shows how they express "
        "themselves and their unique gifts to the world. "
        "Use this when the user asks about their talents, abilities, skills, "
        "or provides their full name. "
        "Returns a number between 1-9 or master numbers 11, 22, 33."
    ),
    properties={
        "full_name": {
            "type": "string",
            "description": (
                "User's full birth name as it appears on their birth certificate "
                "(e.g., 'John Michael Smith'). Ask the user for their complete "
                "birth name including first, middle, and last names if not provided. "
                "This should be the name they were given at birth, not a married "
                "name or nickname."
            )
        }
    },
    required=["full_name"]
)

calculate_soul_urge_number_function = FunctionSchema(
    name="calculate_soul_urge_number",
    description=(
        "Calculate the user's Soul Urge number from their full birth name. "
        "The Soul Urge number (also called Heart's Desire) reveals their "
        "inner motivations, desires, and what drives them at a soul level. "
        "It shows what they truly want and need to feel fulfilled. "
        "Use this when the user asks about their inner desires, motivations, "
        "heart's desire, or what truly makes them happy. "
        "Returns a number between 1-9 or master numbers 11, 22, 33."
    ),
    properties={
        "full_name": {
            "type": "string",
            "description": (
                "User's full birth name as it appears on their birth certificate "
                "(e.g., 'Sarah Elizabeth Johnson'). Ask the user for their complete "
                "birth name including first, middle, and last names if not provided. "
                "This should be the name they were given at birth."
            )
        }
    },
    required=["full_name"]
)

get_numerology_interpretation_function = FunctionSchema(
    name="get_numerology_interpretation",
    description=(
        "Retrieve detailed interpretations for a calculated numerology number. "
        "Use this AFTER calculating a number to provide deeper insights. "
        "Returns expert interpretations covering personality, strengths, challenges, "
        "career guidance, relationships, and spiritual path. "
        "Optionally filter by category to get specific types of insights."
    ),
    properties={
        "number_type": {
            "type": "string",
            "enum": ["life_path", "expression", "soul_urge", "birthday", "personal_year"],
            "description": (
                "Type of numerology number. Must be one of: "
                "life_path, expression, soul_urge, birthday, personal_year"
            )
        },
        "number_value": {
            "type": "integer",
            "description": (
                "The calculated numerology number value. "
                "Must be 1-9 or master numbers 11, 22, 33."
            )
        },
        "category": {
            "type": "string",
            "enum": [
                "personality", "strengths", "challenges", "career",
                "relationships", "spiritual_path", "life_purpose", "compatibility"
            ],
            "description": (
                "Optional: Filter interpretations by category. "
                "If not provided, returns all categories."
            )
        }
    },
    required=["number_type", "number_value"]
)

# Create ToolsSchema with all numerology functions
numerology_tools = ToolsSchema(standard_tools=[
    calculate_life_path_function,
    calculate_expression_number_function,
    calculate_soul_urge_number_function,
    get_numerology_interpretation_function
])
