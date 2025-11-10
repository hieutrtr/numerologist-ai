"""
Numerology Function Call Handlers for Pipecat GPT Integration

This module provides handler functions that execute when GPT calls numerology functions
during voice conversations. Handlers bridge the gap between GPT's function calling
(with string/dict arguments) and Python service functions (with typed arguments).

Handler Pattern:
--------------
Each handler follows this pattern:
1. Receive function arguments as strings/primitives from GPT
2. Validate and convert arguments to proper Python types
3. Call underlying service functions
4. Format results as dicts that GPT can understand
5. Handle errors gracefully without crashing the bot

Integration with Pipecat:
-----------------------
These handlers are designed to work with Pipecat's event handler pattern:

```python
# In pipecat_bot.py - Register tools with LLM context
from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS
llm_context.set_tools(NUMEROLOGY_TOOLS)

# Register function call event handler
from src.voice_pipeline.function_handlers import handle_numerology_function

@llm.event_handler("on_function_call")
async def on_function_call(function_name: str, arguments: dict):
    '''Handle GPT function calls for numerology calculations.'''
    result = handle_numerology_function(function_name, arguments)
    return result
```

Return Format:
-------------
Success: {"result_key": value}
Error: {"error": str, "message": str}

All handlers return dicts (never raise exceptions) so the bot can handle errors
conversationally rather than crashing.

References:
----------
- Story 4.3: numerology_functions.py - OpenAI tool definitions
- Story 4.1: numerology_service.py - Calculation implementations
- Story 4.2: NumerologyInterpretation model - Database schema
- Pipecat Docs: https://docs.pipecat.ai/guides/learn/function-calling
"""

from datetime import date, datetime
from typing import Optional, Dict, Any
import logging

from sqlmodel import Session, select

from src.services.numerology_service import (
    calculate_life_path,
    calculate_expression_number,
    calculate_soul_urge_number
)
from src.models.numerology_interpretation import NumerologyInterpretation
from src.core.database import engine

# Set up logger for this module
logger = logging.getLogger(__name__)


def handle_calculate_life_path(birth_date: str) -> dict:
    """
    Handle GPT function call for Life Path number calculation.

    Converts string birth date to Python date object, calls numerology service,
    and returns result in GPT-friendly format.

    Args:
        birth_date: Birth date string in YYYY-MM-DD format (e.g., "1990-05-15")

    Returns:
        dict: Success {"life_path_number": int} or Error {"error": str, "message": str}

    Example:
        >>> handle_calculate_life_path("1990-05-15")
        {"life_path_number": 7}

        >>> handle_calculate_life_path("invalid")
        {"error": "InvalidDate", "message": "Invalid date format..."}
    """
    try:
        logger.info(f"Calculating Life Path number for birth date: {birth_date}")

        # Convert string to date object
        parsed_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # Call service function
        result = calculate_life_path(parsed_date)

        logger.info(f"Successfully calculated Life Path number: {result}")

        return {"life_path_number": result}

    except ValueError as e:
        logger.error(f"Invalid date format: {birth_date}", exc_info=True)
        return {
            "error": "InvalidDate",
            "message": "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)"
        }
    except Exception as e:
        logger.error(f"Unexpected error in handle_calculate_life_path", exc_info=True)
        return {
            "error": "CalculationError",
            "message": "Unable to calculate Life Path number. Please try again."
        }


def handle_calculate_expression(full_name: str) -> dict:
    """
    Handle GPT function call for Expression number calculation.

    Validates full name is non-empty, calls numerology service, and returns
    result in GPT-friendly format.

    Args:
        full_name: Full birth name as string (e.g., "John Michael Smith")

    Returns:
        dict: Success {"expression_number": int} or Error {"error": str, "message": str}

    Example:
        >>> handle_calculate_expression("John Michael Smith")
        {"expression_number": 5}

        >>> handle_calculate_expression("")
        {"error": "InvalidName", "message": "Please provide your full name"}
    """
    try:
        logger.info(f"Calculating Expression number for name")

        # Validate name is non-empty
        if not full_name or not full_name.strip():
            logger.warning("Empty name provided for Expression number calculation")
            return {
                "error": "InvalidName",
                "message": "Please provide your full name"
            }

        # Call service function
        result = calculate_expression_number(full_name)

        logger.info(f"Successfully calculated Expression number: {result}")

        return {"expression_number": result}

    except Exception as e:
        logger.error(f"Error in handle_calculate_expression", exc_info=True)
        return {
            "error": "CalculationError",
            "message": "Unable to calculate Expression number. Please try again."
        }


def handle_calculate_soul_urge(full_name: str) -> dict:
    """
    Handle GPT function call for Soul Urge number calculation.

    Validates full name is non-empty, calls numerology service, and returns
    result in GPT-friendly format.

    Args:
        full_name: Full birth name as string (e.g., "Sarah Elizabeth Johnson")

    Returns:
        dict: Success {"soul_urge_number": int} or Error {"error": str, "message": str}

    Example:
        >>> handle_calculate_soul_urge("Sarah Elizabeth Johnson")
        {"soul_urge_number": 11}

        >>> handle_calculate_soul_urge("")
        {"error": "InvalidName", "message": "Please provide your full name"}
    """
    try:
        logger.info(f"Calculating Soul Urge number for name")

        # Validate name is non-empty
        if not full_name or not full_name.strip():
            logger.warning("Empty name provided for Soul Urge number calculation")
            return {
                "error": "InvalidName",
                "message": "Please provide your full name"
            }

        # Call service function
        result = calculate_soul_urge_number(full_name)

        logger.info(f"Successfully calculated Soul Urge number: {result}")

        return {"soul_urge_number": result}

    except Exception as e:
        logger.error(f"Error in handle_calculate_soul_urge", exc_info=True)
        return {
            "error": "CalculationError",
            "message": "Unable to calculate Soul Urge number. Please try again."
        }


def handle_get_interpretation(
    number_type: str,
    number_value: int,
    category: Optional[str] = None
) -> dict:
    """
    Handle GPT function call for retrieving numerology interpretations.

    Queries database for interpretations matching number type and value,
    optionally filtered by category.

    Args:
        number_type: Type of number (life_path, expression, soul_urge, birthday, personal_year)
        number_value: The numerology number value (1-9 or 11, 22, 33)
        category: Optional category filter (personality, strengths, challenges, etc.)

    Returns:
        dict: Success {"interpretations": [{"category": str, "content": str}]}
              or Error {"error": str, "message": str}

    Example:
        >>> handle_get_interpretation("life_path", 1)
        {"interpretations": [
            {"category": "personality", "content": "Natural born leader..."},
            {"category": "strengths", "content": "Independence and innovation..."}
        ]}

        >>> handle_get_interpretation("life_path", 1, "personality")
        {"interpretations": [{"category": "personality", "content": "Natural born leader..."}]}
    """
    try:
        logger.info(f"Retrieving interpretations for {number_type} {number_value}" +
                   (f" (category: {category})" if category else ""))

        with Session(engine) as session:
            # Build query with required filters
            query = select(NumerologyInterpretation).where(
                NumerologyInterpretation.number_type == number_type,
                NumerologyInterpretation.number_value == number_value
            )

            # Add optional category filter
            if category:
                query = query.where(NumerologyInterpretation.category == category)

            # Execute query
            results = session.exec(query).all()

            # Convert to GPT-friendly format
            interpretations = [
                {"category": interp.category, "content": interp.content}
                for interp in results
            ]

            logger.info(f"Retrieved {len(interpretations)} interpretation(s)")

            return {"interpretations": interpretations}

    except Exception as e:
        logger.error(f"Database error in handle_get_interpretation", exc_info=True)
        return {
            "error": "DatabaseError",
            "message": "Unable to retrieve interpretations. Please try again."
        }


def handle_numerology_function(function_name: str, arguments: dict) -> dict:
    """
    Main router function that dispatches GPT function calls to appropriate handlers.

    This function is called by Pipecat's event handler when GPT invokes a numerology
    function. It routes to the appropriate handler based on function name and
    extracts arguments from the dict.

    Args:
        function_name: Name of function GPT wants to call
        arguments: Dict of arguments GPT provided

    Returns:
        dict: Result from handler (success or error dict)

    Supported Functions:
        - calculate_life_path: {"birth_date": "YYYY-MM-DD"}
        - calculate_expression_number: {"full_name": "Full Name"}
        - calculate_soul_urge_number: {"full_name": "Full Name"}
        - get_numerology_interpretation: {"number_type": str, "number_value": int, "category": str?}

    Example:
        >>> handle_numerology_function("calculate_life_path", {"birth_date": "1990-05-15"})
        {"life_path_number": 7}

        >>> handle_numerology_function("unknown_function", {})
        {"error": "UnknownFunction", "message": "Function unknown_function not found"}
    """
    try:
        logger.info(f"Handling function call: {function_name} with arguments: {arguments}")

        # Route to appropriate handler
        if function_name == "calculate_life_path":
            birth_date = arguments["birth_date"]
            return handle_calculate_life_path(birth_date)

        elif function_name == "calculate_expression_number":
            full_name = arguments["full_name"]
            return handle_calculate_expression(full_name)

        elif function_name == "calculate_soul_urge_number":
            full_name = arguments["full_name"]
            return handle_calculate_soul_urge(full_name)

        elif function_name == "get_numerology_interpretation":
            number_type = arguments["number_type"]
            number_value = arguments["number_value"]
            category = arguments.get("category")  # Optional parameter
            return handle_get_interpretation(number_type, number_value, category)

        else:
            logger.error(f"Unknown function name: {function_name}")
            return {
                "error": "UnknownFunction",
                "message": f"Function {function_name} not found"
            }

    except KeyError as e:
        logger.error(f"Missing required argument: {e}", exc_info=True)
        return {
            "error": "MissingArgument",
            "message": f"Missing required parameter: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in handle_numerology_function", exc_info=True)
        return {
            "error": "HandlerError",
            "message": "Unable to process function call. Please try again."
        }
