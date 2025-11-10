# Story 4.4: Function Call Handler Implementation

Status: review

## Story

As a backend developer,
I want handlers that execute when GPT calls numerology functions,
So that calculations happen and results return to the AI.

## Acceptance Criteria

### AC1: Handler File Created
- File created at `backend/src/voice_pipeline/function_handlers.py`
- Module exports handler functions for all numerology tools
- Comprehensive module docstring explaining handler pattern and Pipecat integration
- Type hints for all functions

### AC2: Life Path Handler Function
- Function: `handle_calculate_life_path(birth_date: str) -> dict`
- Converts string birth_date (YYYY-MM-DD) to Python date object
- Calls `numerology_service.calculate_life_path(birth_date: date)`
- Returns dict with calculated number: `{"life_path_number": int}`
- Handles invalid date formats with clear error messages

### AC3: Expression Number Handler Function
- Function: `handle_calculate_expression(full_name: str) -> dict`
- Validates full_name is non-empty string
- Calls `numerology_service.calculate_expression_number(full_name: str)`
- Returns dict with calculated number: `{"expression_number": int}`
- Handles empty/invalid names with clear error messages

### AC4: Soul Urge Number Handler Function
- Function: `handle_calculate_soul_urge(full_name: str) -> dict`
- Validates full_name is non-empty string
- Calls `numerology_service.calculate_soul_urge_number(full_name: str)`
- Returns dict with calculated number: `{"soul_urge_number": int}`
- Handles empty/invalid names with clear error messages

### AC5: Interpretation Retrieval Handler Function
- Function: `handle_get_interpretation(number_type: str, number_value: int, category: str = None) -> dict`
- Queries database using `NumerologyInterpretation` model
- Filters by number_type and number_value (required)
- Optionally filters by category if provided
- Returns dict with interpretations: `{"interpretations": [{"category": str, "content": str}]}`
- Handles missing interpretations gracefully

### AC6: Main Router Function
- Function: `handle_numerology_function(function_name: str, arguments: dict) -> dict`
- Routes function calls to appropriate handler based on function_name
- Extracts arguments from dict and passes to handlers
- Maps function names:
  - "calculate_life_path" → handle_calculate_life_path
  - "calculate_expression_number" → handle_calculate_expression
  - "calculate_soul_urge_number" → handle_calculate_soul_urge
  - "get_numerology_interpretation" → handle_get_interpretation
- Returns handler result dict

### AC7: Error Handling
- All handlers catch exceptions and return error dicts
- Error format: `{"error": str, "message": str}`
- Specific error messages for:
  - Invalid date formats
  - Empty/invalid names
  - Missing required arguments
  - Database query failures
  - Unknown function names
- Errors logged but don't crash bot

### AC8: Execution Logging
- All handler calls logged with function name and arguments
- Successful executions logged with results
- Errors logged with full exception details
- Use Python logging module with appropriate levels (INFO, ERROR)
- Log format includes timestamp, function name, and user-friendly description

## Tasks / Subtasks

### Task 1: Create Function Handlers Module (AC: #1)
- [x] **1.1** Create file `backend/src/voice_pipeline/function_handlers.py`
- [x] **1.2** Add module docstring explaining:
  - Purpose: Handler functions for GPT function calls
  - Pattern: Convert GPT arguments → call service → return GPT-friendly result
  - Integration with Pipecat event handlers
  - Reference to Story 4.3 (tool definitions)
- [x] **1.3** Import necessary modules:
  - `from datetime import date, datetime`
  - `from typing import Optional, Dict, Any`
  - `import logging`
  - `from sqlmodel import Session, select`
  - `from src.services.numerology_service import calculate_life_path, calculate_expression_number, calculate_soul_urge_number`
  - `from src.models.numerology_interpretation import NumerologyInterpretation`
  - `from src.core.database import engine`
- [x] **1.4** Set up logger: `logger = logging.getLogger(__name__)`

### Task 2: Implement Life Path Handler (AC: #2)
- [x] **2.1** Define function signature: `def handle_calculate_life_path(birth_date: str) -> dict:`
- [x] **2.2** Add docstring with parameter and return value documentation
- [x] **2.3** Parse birth_date string to date object using `datetime.strptime(birth_date, "%Y-%m-%d").date()`
- [x] **2.4** Call `calculate_life_path(parsed_date)`
- [x] **2.5** Return success dict: `{"life_path_number": result}`
- [x] **2.6** Add try/except for ValueError (invalid date format)
- [x] **2.7** Return error dict on failure: `{"error": "InvalidDate", "message": "..."}`
- [x] **2.8** Log execution: INFO on success, ERROR on failure

### Task 3: Implement Expression Number Handler (AC: #3)
- [x] **3.1** Define function signature: `def handle_calculate_expression(full_name: str) -> dict:`
- [x] **3.2** Add docstring
- [x] **3.3** Validate full_name is non-empty (strip whitespace first)
- [x] **3.4** Call `calculate_expression_number(full_name)`
- [x] **3.5** Return success dict: `{"expression_number": result}`
- [x] **3.6** Add try/except for validation and calculation errors
- [x] **3.7** Return error dict on failure
- [x] **3.8** Log execution

### Task 4: Implement Soul Urge Number Handler (AC: #4)
- [x] **4.1** Define function signature: `def handle_calculate_soul_urge(full_name: str) -> dict:`
- [x] **4.2** Add docstring
- [x] **4.3** Validate full_name is non-empty
- [x] **4.4** Call `calculate_soul_urge_number(full_name)`
- [x] **4.5** Return success dict: `{"soul_urge_number": result}`
- [x] **4.6** Add try/except for errors
- [x] **4.7** Return error dict on failure
- [x] **4.8** Log execution

### Task 5: Implement Interpretation Retrieval Handler (AC: #5)
- [x] **5.1** Define function signature: `def handle_get_interpretation(number_type: str, number_value: int, category: Optional[str] = None) -> dict:`
- [x] **5.2** Add docstring explaining database query pattern
- [x] **5.3** Create database session: `with Session(engine) as session:`
- [x] **5.4** Build query filtering by number_type and number_value
- [x] **5.5** If category provided, add category filter to query
- [x] **5.6** Execute query and fetch all matching interpretations
- [x] **5.7** Convert results to list of dicts: `[{"category": interp.category, "content": interp.content} for interp in results]`
- [x] **5.8** Return success dict: `{"interpretations": list_of_dicts}`
- [x] **5.9** Handle case where no interpretations found (return empty list, not error)
- [x] **5.10** Add try/except for database errors
- [x] **5.11** Log execution with result count

### Task 6: Implement Main Router Function (AC: #6)
- [x] **6.1** Define function signature: `def handle_numerology_function(function_name: str, arguments: dict) -> dict:`
- [x] **6.2** Add docstring explaining routing pattern
- [x] **6.3** Log incoming function call: `logger.info(f"Handling function call: {function_name}")`
- [x] **6.4** Create if/elif chain for function routing:
  - If `function_name == "calculate_life_path"`: extract birth_date, call handler
  - Elif `function_name == "calculate_expression_number"`: extract full_name, call handler
  - Elif `function_name == "calculate_soul_urge_number"`: extract full_name, call handler
  - Elif `function_name == "get_numerology_interpretation"`: extract parameters, call handler
- [x] **6.5** Add else clause for unknown function names
- [x] **6.6** Return error dict for unknown functions: `{"error": "UnknownFunction", "message": f"Function {function_name} not found"}`
- [x] **6.7** Add try/except for missing arguments (KeyError)
- [x] **6.8** Log routing errors

### Task 7: Add Comprehensive Error Handling (AC: #7)
- [x] **7.1** Review all handlers and ensure try/except blocks catch specific exceptions
- [x] **7.2** Ensure error dicts have consistent format: `{"error": str, "message": str}`
- [x] **7.3** Add helpful error messages for each error type:
  - Date parsing: "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)"
  - Empty name: "Please provide your full name"
  - Missing arguments: "Missing required parameter: {param_name}"
  - Database errors: "Unable to retrieve interpretations. Please try again"
- [x] **7.4** Ensure errors don't expose internal implementation details
- [x] **7.5** Test error paths by passing invalid inputs

### Task 8: Add Execution Logging (AC: #8)
- [x] **8.1** Add INFO log at start of each handler: `logger.info(f"Calculating {type} for input: {sanitized_input}")`
- [x] **8.2** Add INFO log on success: `logger.info(f"Successfully calculated {type}: result={result}")`
- [x] **8.3** Add ERROR log on failure: `logger.error(f"Error in {function}: {error}", exc_info=True)`
- [x] **8.4** Sanitize sensitive data in logs (don't log full names/dates if privacy concern)
- [x] **8.5** Use structured logging format for easier parsing
- [x] **8.6** Verify logs appear in console/file during testing

### Task 9: Wire Function Calling into Pipecat Bot (AC: #6, integration)
- [x] **9.1** Open `backend/src/voice_pipeline/pipecat_bot.py`
- [x] **9.2** Import NUMEROLOGY_TOOLS: `from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS`
- [x] **9.3** Import handler router: `from src.voice_pipeline.function_handlers import handle_numerology_function`
- [x] **9.4** Find where `llm_context = OpenAILLMContext(messages=messages)` is created (around line 216)
- [x] **9.5** Add tools to context: `llm_context.set_tools(NUMEROLOGY_TOOLS)` right after context creation
- [x] **9.6** Register function call event handler with LLM service:
  ```python
  @llm.event_handler("on_function_call")
  async def on_function_call(function_name: str, arguments: dict):
      """Handle GPT function calls for numerology calculations."""
      logger.info(f"Function call received: {function_name}")
      result = handle_numerology_function(function_name, arguments)
      return result
  ```
- [x] **9.7** Place event handler registration after LLM service initialization but before pipeline creation
- [x] **9.8** Verify imports are correct and no circular dependencies

### Task 10: Testing and Validation (AC: all)
- [x] **10.1** Test handle_calculate_life_path with valid date: "1990-05-15"
- [x] **10.2** Test handle_calculate_life_path with invalid date: "invalid"
- [x] **10.3** Test handle_calculate_expression with valid name: "John Michael Smith"
- [x] **10.4** Test handle_calculate_expression with empty name: ""
- [x] **10.5** Test handle_calculate_soul_urge with valid name
- [x] **10.6** Test handle_get_interpretation with valid parameters (number_type="life_path", number_value=1)
- [x] **10.7** Test handle_get_interpretation with category filter
- [x] **10.8** Test handle_numerology_function router with all function names
- [x] **10.9** Test error handling: missing arguments, unknown function names
- [x] **10.10** Verify all functions return dicts (not raise exceptions)
- [x] **10.11** Verify log output for success and error cases
- [x] **10.12** Run integration test: function_name → router → handler → service → result
- [x] **10.13** Test end-to-end: Start bot, verify tools registered, verify function call handler responds

## Dev Notes

### Handler Pattern

**Purpose:**
Handlers bridge the gap between GPT function calls (with string/dict arguments) and Python service functions (with typed arguments). They:
1. Receive function arguments as strings/primitives from GPT
2. Validate and convert arguments to proper Python types
3. Call underlying service functions
4. Format results as dicts that GPT can understand
5. Handle errors gracefully without crashing the bot

**Pattern Example:**
```python
def handle_calculate_life_path(birth_date: str) -> dict:
    """
    Handle GPT function call for Life Path calculation.

    Args:
        birth_date: Birth date string in YYYY-MM-DD format from GPT

    Returns:
        dict: Success {"life_path_number": int} or Error {"error": str, "message": str}
    """
    try:
        # 1. Validate and convert input
        parsed_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

        # 2. Call service function
        result = calculate_life_path(parsed_date)

        # 3. Log success
        logger.info(f"Calculated Life Path: {result} for date: {birth_date}")

        # 4. Return GPT-friendly dict
        return {"life_path_number": result}

    except ValueError as e:
        # 5. Handle errors gracefully
        logger.error(f"Invalid date format: {birth_date}", exc_info=True)
        return {
            "error": "InvalidDate",
            "message": "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)"
        }
```

### Pipecat Integration Pattern

**Integration with pipecat_bot.py (Task 9):**
This story creates the handlers AND wires them into pipecat_bot.py using Pipecat's function calling pattern:

**Step 1: Register Tools with LLM Context**
```python
# In pipecat_bot.py - after creating llm_context
from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS

llm_context = OpenAILLMContext(messages=messages)
llm_context.set_tools(NUMEROLOGY_TOOLS)  # Register numerology tools
```

**Step 2: Register Function Call Event Handler**
```python
# In pipecat_bot.py - after LLM service initialization
from src.voice_pipeline.function_handlers import handle_numerology_function

@llm.event_handler("on_function_call")
async def on_function_call(function_name: str, arguments: dict):
    """
    Pipecat calls this when GPT invokes a function.

    Args:
        function_name: Name of function GPT wants to call (e.g., "calculate_life_path")
        arguments: Dict of arguments GPT provided (e.g., {"birth_date": "1990-05-15"})

    Returns:
        dict: Result from handler to send back to GPT
    """
    logger.info(f"Function call received: {function_name}")
    result = handle_numerology_function(function_name, arguments)
    return result
```

**Reference:** https://docs.pipecat.ai/guides/learn/function-calling

### Return Format for GPT

**Success Format:**
```python
{
    "life_path_number": 3,
    "expression_number": 7,
    "soul_urge_number": 11,
    "interpretations": [
        {"category": "personality", "content": "You are a natural-born leader..."},
        {"category": "strengths", "content": "Your greatest strengths..."}
    ]
}
```

**Error Format:**
```python
{
    "error": "InvalidDate",
    "message": "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)"
}
```

GPT will receive these dicts as tool call results and can:
- Announce the calculated numbers to the user
- Read interpretation content naturally in conversation
- Handle errors by asking for corrected input

### Database Query Pattern

**From Story 4.2 (NumerologyInterpretation model):**
```python
from sqlmodel import Session, select
from src.core.database import engine
from src.models.numerology_interpretation import NumerologyInterpretation

def handle_get_interpretation(number_type: str, number_value: int, category: Optional[str] = None) -> dict:
    try:
        with Session(engine) as session:
            # Build query with required filters
            query = select(NumerologyInterpretation).where(
                NumerologyInterpretation.number_type == number_type,
                NumerologyInterpretation.number_value == number_value
            )

            # Add optional category filter
            if category:
                query = query.where(NumerologyInterpretation.category == category)

            # Execute and fetch results
            results = session.exec(query).all()

            # Convert to GPT-friendly format
            interpretations = [
                {"category": interp.category, "content": interp.content}
                for interp in results
            ]

            logger.info(f"Retrieved {len(interpretations)} interpretations for {number_type} {number_value}")

            return {"interpretations": interpretations}

    except Exception as e:
        logger.error(f"Database error in get_interpretation", exc_info=True)
        return {
            "error": "DatabaseError",
            "message": "Unable to retrieve interpretations. Please try again."
        }
```

### Error Handling Strategy

**Graceful Degradation:**
- Handlers never raise exceptions to the bot (would crash conversation)
- All errors returned as dicts with "error" and "message" keys
- GPT can handle errors conversationally: "I'm sorry, I didn't understand that date format. Could you provide it as YYYY-MM-DD?"

**Error Categories:**
1. **Input Validation Errors**: Invalid formats, empty strings, out-of-range values
2. **Service Errors**: Unexpected calculation failures (rare, since functions are pure)
3. **Database Errors**: Connection failures, query errors, missing data
4. **Routing Errors**: Unknown function names, missing arguments

**Logging Strategy:**
- INFO: Successful operations (function called, result returned)
- WARNING: Handled errors (invalid input, missing data)
- ERROR: Unexpected failures (database errors, uncaught exceptions)

### Type Conversion Notes

**String to Date:**
```python
from datetime import datetime

# GPT sends: "1990-05-15" (string)
# Handler converts: datetime.strptime(birth_date, "%Y-%m-%d").date()
# Service receives: date(1990, 5, 15) (date object)
```

**Why string in GPT tools, date in service?**
- OpenAI function calling only supports primitive JSON types (string, int, bool)
- Python date objects are more precise for calculations
- Handlers perform the type conversion bridge

### Learnings from Previous Story

**From Story 4-3-gpt-function-calling-definitions (Status: done)**

**Tool Definitions Available:**
- `numerology_functions.py` at `backend/src/voice_pipeline/numerology_functions.py`
- 4 tools defined: calculate_life_path, calculate_expression_number, calculate_soul_urge_number, get_numerology_interpretation
- NUMEROLOGY_TOOLS list exported for Pipecat integration

**Function Signatures Expected by GPT:**
1. **calculate_life_path**: Expects `{"birth_date": "YYYY-MM-DD"}` (string)
2. **calculate_expression_number**: Expects `{"full_name": "Full Name"}` (string)
3. **calculate_soul_urge_number**: Expects `{"full_name": "Full Name"}` (string)
4. **get_numerology_interpretation**: Expects `{"number_type": "life_path", "number_value": 1, "category": "personality"}` (category optional)

**Integration Notes:**
- Tool descriptions guide GPT on when to call each function
- Parameter descriptions help GPT extract correct data from user conversation
- Enum values match database schema (life_path, expression, soul_urge, birthday, personal_year)
- Category parameter optional (allows retrieving all categories or specific one)

**Handler Implementation Must Match:**
- Handler parameter names must match tool definition parameter names
- Handler return format must be dict (GPT expects JSON-serializable objects)
- Handlers convert string inputs to proper types (string → date, etc.)

[Source: stories/4-3-gpt-function-calling-definitions.md#Completion-Notes-List]

**From Story 4-1-numerology-calculation-functions (Status: done)**

**Service Functions Available:**
- `numerology_service.py` at `backend/src/services/numerology_service.py`
- Functions: calculate_life_path(birth_date: date), calculate_expression_number(full_name: str), calculate_soul_urge_number(full_name: str)
- MASTER_NUMBERS constant: {11, 22, 33}
- All functions pure (no side effects)

**Integration Notes:**
- Handlers call these service functions after type conversion
- Service functions expect proper Python types (date, str)
- Service functions return int (1-9, 11, 22, 33)

[Source: stories/4-1-numerology-calculation-functions.md#Dev-Agent-Record]

**From Story 4-2-numerology-knowledge-base-schema-seeding (Status: done)**

**Database Model Available:**
- `NumerologyInterpretation` model at `backend/src/models/numerology_interpretation.py`
- 156 interpretations seeded
- Query pattern: Filter by (number_type, number_value) with optional category
- Use synchronous `Session(engine)` pattern (not async)

**Integration Notes:**
- handle_get_interpretation queries this database
- Enum values in tool definitions match database schema exactly
- Return multiple interpretations as list of dicts

[Source: stories/4-2-numerology-knowledge-base-schema-seeding.md#Completion-Notes-List]

### References

- [Source: docs/epics.md#Story-4.4] - Story definition and acceptance criteria
- [Source: docs/architecture.md#Voice-Pipeline-Patterns] - Pipecat event handler pattern
- [Source: backend/src/voice_pipeline/numerology_functions.py] - Tool definitions (Story 4.3)
- [Source: backend/src/services/numerology_service.py] - Calculation functions (Story 4.1)
- [Source: backend/src/models/numerology_interpretation.py] - Database model (Story 4.2)
- [Source: backend/src/voice_pipeline/pipecat_bot.py] - Pipecat bot implementation (Story 3.3)

## Dev Agent Record

### Context Reference

- **Story Context**: [4-4-function-call-handler-implementation.context.xml](./4-4-function-call-handler-implementation.context.xml) - Generated 2025-11-10
  - Documentation artifacts (Architecture Pipecat patterns, Epic 4 Story 4.4, Stories 4.1-4.3 learnings)
  - Code artifacts (numerology_functions.py tool definitions, numerology_service.py functions, NumerologyInterpretation model, database engine, pipecat_bot.py)
  - Interfaces (Handler functions, service functions, database model, NUMEROLOGY_TOOLS)
  - Development constraints (Handler return format, parameter matching, type conversion, graceful error handling, database session pattern, logging standards)
  - Test validation approach (pytest patterns, test success/error paths, verify dict returns, test type conversion, test database queries)

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

### Completion Notes List

**Implementation Summary (2025-11-10):**
- Created comprehensive function_handlers.py module (367 lines) with 5 handler functions
- All handlers follow graceful error handling pattern (return error dicts, never raise exceptions)
- Implemented type conversion bridge: GPT string arguments → Python typed service calls
- Database integration with SQLModel for interpretation retrieval
- Comprehensive logging at INFO/ERROR levels with exc_info for debugging
- Successfully wired function calling into pipecat_bot.py using Pipecat event handler pattern
- Fixed circular import issues by using deferred imports inside run_bot function
- Created 37 comprehensive tests covering all ACs (100% passing)
- Tests validate: handlers return dicts, error handling, logging, routing, database queries, full integration flow

**Technical Achievements:**
- All 5 handler functions (life_path, expression, soul_urge, interpretation, router) implemented with proper error handling
- Router correctly dispatches to handlers based on function_name
- Date parsing (string → date object) works correctly with helpful error messages
- Name validation ensures non-empty inputs before calculation
- Database queries use Session(engine) pattern with optional category filtering
- Event handler registered with @llm.event_handler("on_function_call") decorator
- Tools registered with llm_context.set_tools(NUMEROLOGY_TOOLS)
- All error messages user-friendly, don't expose implementation details

**Test Results:**
- 37/37 handler tests passing
- Covers all 8 acceptance criteria
- Test categories: handlers (14 tests), interpretation (5 tests), routing (8 tests), error handling (3 tests), integration (4 tests), logging (3 tests)
- No regressions in existing numerology service tests (38/38 passing)

### File List
- backend/src/voice_pipeline/function_handlers.py (created, 367 lines)
- backend/src/voice_pipeline/pipecat_bot.py (modified, added function calling integration)
- backend/tests/voice_pipeline/test_function_handlers.py (created, 470 lines, 37 tests)
- backend/tests/voice_pipeline/__init__.py (created)
