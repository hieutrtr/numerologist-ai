"""
Numerology Function Call Handlers for Pipecat Integration

This module provides async handler functions that execute when the LLM calls numerology
functions during voice conversations. Handlers use Pipecat's FunctionCallParams pattern
with result callbacks for proper integration with the voice pipeline.

Handler Pattern:
--------------
Each handler follows Pipecat's async callback pattern:
1. Receive FunctionCallParams containing function name, arguments, context, and callback
2. Extract and validate arguments from params.arguments
3. Call underlying service functions
4. Return results via params.result_callback()
5. Handle errors gracefully without crashing the bot

Integration with Pipecat:
-----------------------
These handlers are designed to work with Pipecat's function registration:

```python
from pipecat.services.azure import AzureLLMService
from src.voice_pipeline.function_handlers import (
    handle_calculate_life_path,
    handle_calculate_expression,
    handle_calculate_soul_urge,
    handle_get_interpretation
)

llm = AzureLLMService(...)

llm.register_function("calculate_life_path", handle_calculate_life_path)
llm.register_function("calculate_expression_number", handle_calculate_expression)
llm.register_function("calculate_soul_urge_number", handle_calculate_soul_urge)
llm.register_function("get_numerology_interpretation", handle_get_interpretation)
```

Return Pattern:
-------------
Results are returned via the async callback:
```python
await params.result_callback({"result_key": value})
```

References:
----------
- Pipecat Function Calling: https://docs.pipecat.ai/guides/learn/function-calling
- Story 4.3: numerology_functions.py - Function schemas
- Story 4.1: numerology_service.py - Calculation implementations
- Story 4.2: NumerologyInterpretation model - Database schema
"""

from datetime import datetime
import logging

from sqlmodel import Session, select
from pipecat.services.llm_service import FunctionCallParams, FunctionCallResultProperties

from src.services.numerology_service import (
    calculate_life_path,
    calculate_expression_number,
    calculate_soul_urge_number
)
from src.models.numerology_interpretation import NumerologyInterpretation
from src.core.database import engine

# Set up logger for this module
logger = logging.getLogger(__name__)


async def handle_calculate_life_path(params: FunctionCallParams):
    """
    Handle LLM function call for Life Path number calculation.

    Converts string birth date to Python date object, calls numerology service,
    and returns result via callback.

    Args:
        params: FunctionCallParams containing:
            - arguments: {"birth_date": "YYYY-MM-DD"}
            - result_callback: Async function to return results

    Returns:
        Via callback: {"life_path_number": int} or {"error": str, "message": str}

    Example:
        LLM calls with {"birth_date": "1990-05-15"}
        → Returns {"life_path_number": 7}
    """
    try:
        birth_date = params.arguments.get("birth_date")
        logger.info(f"Calculating Life Path number for birth date: {birth_date}")

        # Convert string to date object
        parsed_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # Call service function
        result = calculate_life_path(parsed_date)

        logger.info(f"Successfully calculated Life Path number: {result}")

        # Tell Pipecat to run the LLM after this function result
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback({"life_path_number": result}, properties=properties)

    except ValueError as e:
        logger.error(f"Invalid date format: {birth_date}", exc_info=True)
        await params.result_callback({
            "error": "InvalidDate",
            "message": "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)"
        })
    except Exception as e:
        logger.error(f"Unexpected error in handle_calculate_life_path", exc_info=True)
        await params.result_callback({
            "error": "CalculationError",
            "message": "Unable to calculate Life Path number. Please try again."
        })


async def handle_calculate_expression(params: FunctionCallParams):
    """
    Handle LLM function call for Expression number calculation.

    Validates full name is non-empty, calls numerology service, and returns
    result via callback.

    Args:
        params: FunctionCallParams containing:
            - arguments: {"full_name": "Full Name"}
            - result_callback: Async function to return results

    Returns:
        Via callback: {"expression_number": int} or {"error": str, "message": str}

    Example:
        LLM calls with {"full_name": "John Michael Smith"}
        → Returns {"expression_number": 5}
    """
    try:
        full_name = params.arguments.get("full_name")
        logger.info(f"Calculating Expression number for name")

        # Validate name is non-empty
        if not full_name or not full_name.strip():
            logger.warning("Empty name provided for Expression number calculation")
            await params.result_callback({
                "error": "InvalidName",
                "message": "Please provide your full name"
            })
            return

        # Call service function
        result = calculate_expression_number(full_name)

        logger.info(f"Successfully calculated Expression number: {result}")

        # Tell Pipecat to run the LLM after this function result
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback({"expression_number": result}, properties=properties)

    except Exception as e:
        logger.error(f"Error in handle_calculate_expression", exc_info=True)
        await params.result_callback({
            "error": "CalculationError",
            "message": "Unable to calculate Expression number. Please try again."
        })


async def handle_calculate_soul_urge(params: FunctionCallParams):
    """
    Handle LLM function call for Soul Urge number calculation.

    Validates full name is non-empty, calls numerology service, and returns
    result via callback.

    Args:
        params: FunctionCallParams containing:
            - arguments: {"full_name": "Full Name"}
            - result_callback: Async function to return results

    Returns:
        Via callback: {"soul_urge_number": int} or {"error": str, "message": str}

    Example:
        LLM calls with {"full_name": "Sarah Elizabeth Johnson"}
        → Returns {"soul_urge_number": 11}
    """
    try:
        full_name = params.arguments.get("full_name")
        logger.info(f"Calculating Soul Urge number for name")

        # Validate name is non-empty
        if not full_name or not full_name.strip():
            logger.warning("Empty name provided for Soul Urge number calculation")
            await params.result_callback({
                "error": "InvalidName",
                "message": "Please provide your full name"
            })
            return

        # Call service function
        result = calculate_soul_urge_number(full_name)

        logger.info(f"Successfully calculated Soul Urge number: {result}")

        # Tell Pipecat to run the LLM after this function result
        properties = FunctionCallResultProperties(run_llm=True)
        await params.result_callback({"soul_urge_number": result}, properties=properties)

    except Exception as e:
        logger.error(f"Error in handle_calculate_soul_urge", exc_info=True)
        await params.result_callback({
            "error": "CalculationError",
            "message": "Unable to calculate Soul Urge number. Please try again."
        })


async def handle_get_interpretation(params: FunctionCallParams):
    """
    Handle LLM function call for retrieving numerology interpretations.

    Queries database for interpretations matching number type and value,
    optionally filtered by category.

    Args:
        params: FunctionCallParams containing:
            - arguments: {
                "number_type": str,
                "number_value": int,
                "category": str (optional)
              }
            - result_callback: Async function to return results

    Returns:
        Via callback: {"interpretations": [{"category": str, "content": str}]}
                     or {"error": str, "message": str}

    Example:
        LLM calls with {"number_type": "life_path", "number_value": 1}
        → Returns {"interpretations": [
            {"category": "personality", "content": "Natural born leader..."},
            {"category": "strengths", "content": "Independence..."}
        ]}
    """
    try:
        number_type = params.arguments.get("number_type")
        number_value = params.arguments.get("number_value")
        category = params.arguments.get("category")  # Optional

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

            # Convert to LLM-friendly format
            interpretations = [
                {"category": interp.category, "content": interp.content}
                for interp in results
            ]

            logger.info(f"Retrieved {len(interpretations)} interpretation(s)")

            # Tell Pipecat to run the LLM after this function result
            properties = FunctionCallResultProperties(run_llm=True)
            await params.result_callback({"interpretations": interpretations}, properties=properties)

    except Exception as e:
        logger.error(f"Database error in handle_get_interpretation", exc_info=True)
        await params.result_callback({
            "error": "DatabaseError",
            "message": "Unable to retrieve interpretations. Please try again."
        })
