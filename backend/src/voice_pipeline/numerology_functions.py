"""
Numerology Function Calling Definitions for OpenAI GPT Integration

This module provides OpenAI-formatted function calling definitions (tools) that enable
the AI to invoke numerology calculations and retrieve interpretations during voice
conversations. These tool definitions follow OpenAI's function calling format with
JSON Schema parameters, allowing GPT to understand when and how to use each tool.

The tools defined here bridge the gap between conversational AI (GPT) and the
numerology engine, enabling the AI to:
1. Calculate numerology numbers from user-provided data (birth date, name)
2. Retrieve expert interpretations from the knowledge base
3. Provide personalized numerology guidance in natural conversation

Integration with Pipecat:
-----------------------
These tools are designed to work with Pipecat's OpenAILLMContext. To integrate:

```python
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS

# Create LLM context with system messages
llm_context = OpenAILLMContext(messages=[
    {"role": "system", "content": system_prompt}
])

# Register numerology tools
llm_context.set_tools(NUMEROLOGY_TOOLS)

# Register function handlers (Story 4.4)
@llm.event_handler("on_function_call")
async def handle_function_call(function_name: str, arguments: dict):
    # Route to appropriate handler
    return await execute_numerology_function(function_name, arguments)
```

OpenAI Tool Format:
-------------------
Each tool follows this structure:
{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "Clear description for GPT",
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param_name"]
        }
    }
}

References:
-----------
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- Story 4.1: numerology_service.py - Calculation implementations
- Story 4.2: NumerologyInterpretation model - Database schema
- Story 4.4: function_handlers.py - Handler implementations (next story)
"""

# OpenAI tool definitions for numerology calculations and interpretation retrieval
NUMEROLOGY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_life_path",
            "description": (
                "Calculate the user's Life Path number from their birth date. "
                "The Life Path number reveals their life purpose, natural tendencies, "
                "and the journey they're meant to take in this lifetime. "
                "Use this when the user asks about their life path, purpose, destiny, "
                "or provides their birth date. "
                "Returns a number between 1-9 or master numbers 11, 22, 33."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_date": {
                        "type": "string",
                        "format": "date",
                        "description": (
                            "User's birth date in YYYY-MM-DD format (e.g., 1990-05-15). "
                            "Ask the user for their complete birth date including year, "
                            "month, and day if not provided."
                        )
                    }
                },
                "required": ["birth_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_expression_number",
            "description": (
                "Calculate the user's Expression number from their full birth name. "
                "The Expression number reveals their natural talents, abilities, "
                "and the potential they were born with. It shows how they express "
                "themselves and their unique gifts to the world. "
                "Use this when the user asks about their talents, abilities, skills, "
                "or provides their full name. "
                "Returns a number between 1-9 or master numbers 11, 22, 33."
            ),
            "parameters": {
                "type": "object",
                "properties": {
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
                "required": ["full_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_soul_urge_number",
            "description": (
                "Calculate the user's Soul Urge number from their full birth name. "
                "The Soul Urge number (also called Heart's Desire) reveals their "
                "inner motivations, desires, and what drives them at a soul level. "
                "It shows what they truly want and need to feel fulfilled. "
                "Use this when the user asks about their inner desires, motivations, "
                "heart's desire, or what truly makes them happy. "
                "Returns a number between 1-9 or master numbers 11, 22, 33."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "full_name": {
                        "type": "string",
                        "description": (
                            "User's full birth name as it appears on their birth certificate "
                            "(e.g., 'Sarah Elizabeth Johnson'). Ask the user for their complete "
                            "birth name including first, middle, and last names if not provided. "
                            "This calculation uses the vowels in the name to determine "
                            "inner motivations."
                        )
                    }
                },
                "required": ["full_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_numerology_interpretation",
            "description": (
                "Retrieve expert numerology interpretations for a specific number type "
                "and value. Interpretations provide detailed, actionable guidance about "
                "personality traits, strengths, challenges, career paths, relationships, "
                "and more based on traditional Pythagorean numerology. "
                "Use this after calculating a numerology number to provide detailed "
                "guidance, or when the user asks for more information about a specific "
                "number they already know. "
                "Returns interpretation text in 2-4 sentence format."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "number_type": {
                        "type": "string",
                        "enum": [
                            "life_path",
                            "expression",
                            "soul_urge",
                            "birthday",
                            "personal_year"
                        ],
                        "description": (
                            "Type of numerology number to interpret. Options: "
                            "'life_path' (life purpose and journey), "
                            "'expression' (talents and abilities), "
                            "'soul_urge' (inner desires and motivations), "
                            "'birthday' (special gifts from birth day), "
                            "'personal_year' (current year cycle themes)."
                        )
                    },
                    "number_value": {
                        "type": "integer",
                        "description": (
                            "The numerology number value to interpret. "
                            "Must be 1-9 or master numbers 11, 22, 33. "
                            "This should be the result from a calculation function."
                        )
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "personality",
                            "strengths",
                            "challenges",
                            "career",
                            "relationships",
                            "talents",
                            "abilities",
                            "purpose"
                        ],
                        "description": (
                            "Optional: Specific category of interpretation to retrieve. "
                            "If not provided, returns all available categories. Options: "
                            "'personality' (core traits), "
                            "'strengths' (natural abilities), "
                            "'challenges' (growth areas), "
                            "'career' (professional guidance), "
                            "'relationships' (interpersonal dynamics), "
                            "'talents' (special skills), "
                            "'abilities' (natural capabilities), "
                            "'purpose' (life mission)."
                        )
                    }
                },
                "required": ["number_type", "number_value"]
            }
        }
    }
]
