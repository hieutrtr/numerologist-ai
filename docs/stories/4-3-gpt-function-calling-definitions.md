# Story 4.3: GPT Function Calling Definitions

Status: done

## Story

As a backend developer,
I want GPT function definitions for numerology tools,
So that the AI can call calculation functions during conversation.

## Acceptance Criteria

### AC1: Function Definitions File Created
- File created at `backend/src/voice_pipeline/numerology_functions.py`
- Module exports `NUMEROLOGY_TOOLS` list constant
- Follows OpenAI function calling format specification
- Comprehensive module docstring explaining purpose and usage

### AC2: Life Path Calculation Tool
- Function definition for `calculate_life_path`
- Description explains: "Calculate the user's Life Path number from their birth date. This reveals their life purpose and journey."
- Parameter: `birth_date` (string, format: YYYY-MM-DD, required)
- Parameter has clear description for GPT to understand what data to request
- Schema matches `calculate_life_path()` from `numerology_service.py`

### AC3: Expression Number Calculation Tool
- Function definition for `calculate_expression_number`
- Description explains: "Calculate the user's Expression number from their full birth name. This reveals their natural talents and abilities."
- Parameter: `full_name` (string, required)
- Parameter description guides GPT to request complete birth name
- Schema matches `calculate_expression_number()` from `numerology_service.py`

### AC4: Soul Urge Number Calculation Tool
- Function definition for `calculate_soul_urge_number`
- Description explains: "Calculate the user's Soul Urge number from their full birth name. This reveals their inner desires and motivations."
- Parameter: `full_name` (string, required)
- Schema matches `calculate_soul_urge_number()` from `numerology_service.py`

### AC5: Interpretation Retrieval Tool
- Function definition for `get_numerology_interpretation`
- Description explains: "Retrieve expert numerology interpretations for a specific number type and value."
- Parameters:
  - `number_type` (string, enum: life_path|expression|soul_urge|birthday|personal_year, required)
  - `number_value` (integer, 1-9 or master numbers 11, 22, 33, required)
  - `category` (string, optional, enum: personality|strengths|challenges|career|relationships|talents|abilities|purpose)
- Clear descriptions help GPT choose correct number type and category

### AC6: OpenAI Tool Format Compliance
- All function definitions follow OpenAI's tool calling format:
  ```python
  {
      "type": "function",
      "function": {
          "name": "function_name",
          "description": "Clear description for GPT",
          "parameters": {
              "type": "object",
              "properties": { ... },
              "required": [ ... ]
          }
      }
  }
  ```
- Type annotations use JSON Schema types (string, integer, object, array)
- Required fields marked in `required` array
- Enum values specified where appropriate

### AC7: Integration-Ready Export
- Module exports `NUMEROLOGY_TOOLS` as a list ready for OpenAI context
- Can be imported: `from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS`
- Format matches Pipecat's `OpenAILLMContext.set_tools()` expectations
- Documentation includes integration example with pipecat_bot.py

## Tasks / Subtasks

### Task 1: Create Numerology Functions Module (AC: #1)
- [x] **1.1** Create file `backend/src/voice_pipeline/numerology_functions.py`
- [x] **1.2** Add module docstring explaining:
  - Purpose: GPT function calling definitions for numerology
  - OpenAI tool calling format
  - Integration with Pipecat OpenAILLMContext
  - Reference to Story 4.4 for handler implementation
- [x] **1.3** Import necessary types (if using TypedDict or similar)

### Task 2: Define Life Path Tool (AC: #2)
- [x] **2.1** Create function definition dict for `calculate_life_path`
- [x] **2.2** Write clear description mentioning life purpose and journey
- [x] **2.3** Define `birth_date` parameter:
  - Type: string
  - Format: date (YYYY-MM-DD)
  - Description: "User's birth date in YYYY-MM-DD format"
  - Required: true
- [x] **2.4** Verify schema matches `calculate_life_path(birth_date: date)` signature

### Task 3: Define Expression Number Tool (AC: #3)
- [x] **3.1** Create function definition dict for `calculate_expression_number`
- [x] **3.2** Write description explaining natural talents and abilities
- [x] **3.3** Define `full_name` parameter:
  - Type: string
  - Description: "User's full birth name as it appears on their birth certificate"
  - Required: true
- [x] **3.4** Verify schema matches `calculate_expression_number(full_name: str)` signature

### Task 4: Define Soul Urge Tool (AC: #4)
- [x] **4.1** Create function definition dict for `calculate_soul_urge_number`
- [x] **4.2** Write description explaining inner desires and motivations
- [x] **4.3** Define `full_name` parameter (same as Expression)
- [x] **4.4** Verify schema matches `calculate_soul_urge_number(full_name: str)` signature

### Task 5: Define Interpretation Retrieval Tool (AC: #5)
- [x] **5.1** Create function definition dict for `get_numerology_interpretation`
- [x] **5.2** Write description explaining interpretation retrieval
- [x] **5.3** Define `number_type` parameter:
  - Type: string
  - Enum: ["life_path", "expression", "soul_urge", "birthday", "personal_year"]
  - Description: "Type of numerology number"
  - Required: true
- [x] **5.4** Define `number_value` parameter:
  - Type: integer
  - Description: "Number value (1-9 or master numbers 11, 22, 33)"
  - Required: true
- [x] **5.5** Define `category` parameter:
  - Type: string
  - Enum: ["personality", "strengths", "challenges", "career", "relationships", "talents", "abilities", "purpose"]
  - Description: "Category of interpretation to retrieve (optional)"
  - Required: false

### Task 6: Assemble Tools List and Validate Format (AC: #6, #7)
- [x] **6.1** Create `NUMEROLOGY_TOOLS` list containing all function definitions
- [x] **6.2** Verify each tool follows OpenAI format (type: "function", function: {name, description, parameters})
- [x] **6.3** Validate JSON Schema compliance:
  - parameters.type = "object"
  - properties defined with correct types
  - required array present
  - enum values specified where applicable
- [x] **6.4** Add code example in module docstring showing integration:
  ```python
  # In pipecat_bot.py:
  from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS

  llm_context = OpenAILLMContext(messages=messages)
  llm_context.set_tools(NUMEROLOGY_TOOLS)
  ```

### Task 7: Testing and Validation (AC: all)
- [x] **7.1** Import module successfully: `from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS`
- [x] **7.2** Verify `NUMEROLOGY_TOOLS` is a list
- [x] **7.3** Verify list contains 4 tool definitions (calculate_life_path, calculate_expression_number, calculate_soul_urge_number, get_numerology_interpretation)
- [x] **7.4** Verify each tool has required fields: type, function.name, function.description, function.parameters
- [x] **7.5** Run Python dict validation to ensure no syntax errors
- [x] **7.6** Verify JSON serializable: `import json; json.dumps(NUMEROLOGY_TOOLS)`

## Dev Notes

### OpenAI Function Calling Format

**Tool Definition Structure:**
```python
{
    "type": "function",  # Always "function" for function calling
    "function": {
        "name": "function_name",  # Must match handler function name
        "description": "Clear description that helps GPT decide when to use this tool",
        "parameters": {  # JSON Schema object
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",  # JSON Schema types: string, integer, number, boolean, object, array
                    "description": "What this parameter represents",
                    "enum": ["option1", "option2"]  # Optional: restrict to specific values
                }
            },
            "required": ["param_name"]  # List of required parameter names
        }
    }
}
```

**JSON Schema Types Mapping:**
- Python `str` → JSON Schema `"string"`
- Python `int` → JSON Schema `"integer"`
- Python `float` → JSON Schema `"number"`
- Python `bool` → JSON Schema `"boolean"`
- Python `dict` → JSON Schema `"object"`
- Python `list` → JSON Schema `"array"`
- Python `date` → JSON Schema `"string"` with `"format": "date"`

### Integration with Pipecat

**Pipecat's OpenAILLMContext accepts tools in OpenAI format:**
```python
# In pipecat_bot.py (Story 3.3)
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from src.voice_pipeline.numerology_functions import NUMEROLOGY_TOOLS

# Create context with system messages
llm_context = OpenAILLMContext(messages=[
    {"role": "system", "content": system_prompt}
])

# Register numerology tools (Story 4.3 - this story)
llm_context.set_tools(NUMEROLOGY_TOOLS)

# Later: Register function handlers (Story 4.4)
@llm.event_handler("on_function_call")
async def handle_function_call(function_name: str, arguments: dict):
    # Route to appropriate handler
    return await execute_numerology_function(function_name, arguments)
```

### Description Writing Guidelines

**Good descriptions help GPT understand WHEN to use the tool:**

✅ **Good Example:**
```python
"description": "Calculate the user's Life Path number from their birth date. This reveals their life purpose, natural tendencies, and life journey. Use this when the user asks about their life path, purpose, or provides their birth date."
```

❌ **Bad Example:**
```python
"description": "Calculate life path"  # Too vague, doesn't explain when to use
```

**Key elements:**
1. **What it calculates**: "Calculate the user's Life Path number"
2. **What it reveals**: "This reveals their life purpose and journey"
3. **When to use**: "Use when user asks about life path or provides birth date"
4. **What data is needed**: "from their birth date"

### Parameter Descriptions

**Parameter descriptions should guide GPT on what to request:**

✅ **Good Example:**
```python
"birth_date": {
    "type": "string",
    "format": "date",
    "description": "User's birth date in YYYY-MM-DD format (e.g., 1990-05-15). Ask the user for their complete birth date including year, month, and day."
}
```

❌ **Bad Example:**
```python
"birth_date": {
    "type": "string",
    "description": "Birth date"  # Doesn't explain format or what to ask
}
```

### Numerology Service Functions Reference

**Available Functions (from Story 4.1):**
```python
# backend/src/services/numerology_service.py

def calculate_life_path(birth_date: date) -> int:
    """Calculate Life Path number (1-9, 11, 22, 33) from birth date."""

def calculate_expression_number(full_name: str) -> int:
    """Calculate Expression number (1-9, 11, 22, 33) from full birth name."""

def calculate_soul_urge_number(full_name: str) -> int:
    """Calculate Soul Urge number (1-9, 11, 22, 33) from full birth name."""

def calculate_birthday_number(birth_date: date) -> int:
    """Calculate Birthday number (1-9, 11, 22, 33) from day of birth."""

def calculate_personal_year(birth_date: date, current_year: int) -> int:
    """Calculate Personal Year number (1-9, 11, 22, 33) for current year."""
```

**Note:** This story (4.3) defines GPT tools for 3 calculation functions initially. Birthday and Personal Year calculations can be added in future stories if needed.

### Database Query Pattern for Interpretations

**From Story 4.2 - NumerologyInterpretation Model:**
```python
# backend/src/models/numerology_interpretation.py
class NumerologyInterpretation(SQLModel, table=True):
    __tablename__ = "numerology_interpretation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    number_type: str = Field(index=True)  # life_path, expression, soul_urge, birthday, personal_year
    number_value: int = Field(index=True)  # 1-9, 11, 22, 33
    category: str  # personality, strengths, challenges, career, relationships, talents, abilities, purpose
    content: str  # Interpretation text
    created_at: datetime
    updated_at: datetime
```

**Query Pattern for Story 4.4:**
```python
from sqlmodel import Session, select
from src.models.numerology_interpretation import NumerologyInterpretation

def get_interpretation(session: Session, number_type: str, number_value: int, category: str = None):
    query = select(NumerologyInterpretation).where(
        NumerologyInterpretation.number_type == number_type,
        NumerologyInterpretation.number_value == number_value
    )

    if category:
        query = query.where(NumerologyInterpretation.category == category)

    return session.exec(query).all()
```

### Project Structure Notes

**New Files Created:**
- `backend/src/voice_pipeline/numerology_functions.py` - GPT function definitions

**Files Referenced:**
- `backend/src/voice_pipeline/pipecat_bot.py` - Will integrate NUMEROLOGY_TOOLS in Story 4.4
- `backend/src/services/numerology_service.py` - Contains actual calculation implementations
- `backend/src/models/numerology_interpretation.py` - Database model for interpretations

**Integration Points:**
- Story 4.4 will create handlers that call numerology_service functions when GPT invokes these tools
- Story 4.5 will create system prompts that guide GPT to use these tools appropriately
- Story 4.6 will wire everything together in the conversation endpoint

### Learnings from Previous Story

**From Story 4-2-numerology-knowledge-base-schema-seeding (Status: done)**

**Database Ready for Integration:**
- `NumerologyInterpretation` model available at `backend/src/models/numerology_interpretation.py`
- 156 interpretations seeded in database:
  - Life Path: 60 entries (personality, strengths, challenges, career, relationships)
  - Expression: 36 entries (talents, abilities, purpose)
  - Soul Urge: 24 entries (personality, strengths)
  - Birthday: 12 entries (personality)
  - Personal Year: 24 entries (personality, strengths)
- **Query Pattern**: Use composite index on (number_type, number_value) for performance
- **Master Numbers**: 11, 22, 33 included in all datasets

**Database Access Pattern:**
- Use synchronous `Session(engine)` pattern (not async)
- Import: `from src.core.database import engine`
- Context manager: `with Session(engine) as session:`

**Schema Fields for Tool Definition:**
- `number_type`: String enum (life_path, expression, soul_urge, birthday, personal_year)
- `number_value`: Integer (1-9, 11, 22, 33)
- `category`: String enum (personality, strengths, challenges, career, relationships, talents, abilities, purpose)

**Integration Notes:**
- GPT tool for `get_numerology_interpretation` should accept these exact field names
- Enum values in tool definition should match database schema exactly
- Category parameter should be optional (allows retrieving all categories if not specified)

[Source: stories/4-2-numerology-knowledge-base-schema-seeding.md#Completion-Notes-List]

**From Story 4-1-numerology-calculation-functions (Status: done)**

**Services Available:**
- `numerology_service.py` at `backend/src/services/numerology_service.py`
- 5 calculation functions: calculate_life_path(), calculate_expression_number(), calculate_soul_urge_number(), calculate_birthday_number(), calculate_personal_year()
- MASTER_NUMBERS constant: {11, 22, 33}
- All functions return int (1-9, 11, 22, 33)

**Function Signatures for Tool Definitions:**
- `calculate_life_path(birth_date: date) -> int`
- `calculate_expression_number(full_name: str) -> int`
- `calculate_soul_urge_number(full_name: str) -> int`

**Integration Notes:**
- Tool parameter schemas must match these signatures
- birth_date expects Python date object → GPT tool uses string with format: "date"
- full_name expects complete birth name → Tool description should emphasize "full birth name"

[Source: stories/4-1-numerology-calculation-functions.md#Dev-Agent-Record]

### References

- [Source: docs/epics.md#Story-4.3] - Story definition and acceptance criteria
- [Source: docs/architecture.md#Voice-Pipeline-Patterns] - Pipecat function calling pattern
- [Source: backend/src/voice_pipeline/pipecat_bot.py] - OpenAILLMContext usage pattern
- [Source: backend/src/services/numerology_service.py] - Calculation function signatures
- [Source: backend/src/models/numerology_interpretation.py] - Database schema for interpretations
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) - Official format specification

## Dev Agent Record

### Context Reference

- **Story Context**: [4-3-gpt-function-calling-definitions.context.xml](./4-3-gpt-function-calling-definitions.context.xml) - Generated 2025-11-10
  - Documentation artifacts (Architecture function calling patterns, Epic 4 Story 4.3, PRD AI reasoning, Story 4.1-4.2 learnings)
  - Code artifacts (pipecat_bot.py OpenAILLMContext, numerology_service.py functions, NumerologyInterpretation model)
  - Interfaces (NUMEROLOGY_TOOLS export, OpenAILLMContext.set_tools(), numerology service signatures)
  - Development constraints (OpenAI tool format, JSON Schema types, parameter matching, enum values from database)
  - Test validation approach (pytest patterns, JSON serialization, tool structure validation)

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

### Completion Notes List

#### Implementation Summary (2025-11-10)

**Story 4.3 completed successfully. All acceptance criteria met.**

**Created numerology_functions.py Module:**
- Comprehensive module at `backend/src/voice_pipeline/numerology_functions.py` (218 lines)
- 70-line module docstring with integration examples and OpenAI format explanation
- References to Story 4.1 (numerology_service), Story 4.2 (NumerologyInterpretation), and Story 4.4 (function_handlers)

**Tool Definitions Created (4 total):**
1. **calculate_life_path**: Birth date parameter (string, YYYY-MM-DD format), description explains life purpose and journey, matches numerology_service.calculate_life_path(birth_date: date) signature
2. **calculate_expression_number**: Full name parameter (string), description explains natural talents/abilities, matches numerology_service.calculate_expression_number(full_name: str) signature
3. **calculate_soul_urge_number**: Full name parameter (string), description explains inner desires/motivations, matches numerology_service.calculate_soul_urge_number(full_name: str) signature
4. **get_numerology_interpretation**: Three parameters - number_type (enum matching database schema), number_value (integer 1-9, 11, 22, 33), category (optional enum for specific interpretation)

**OpenAI Format Compliance:**
- All tools follow OpenAI function calling format: type="function", function.name, function.description, function.parameters
- Parameters use JSON Schema types: string, integer, object
- Enum values match database schema exactly (life_path, expression, soul_urge, birthday, personal_year for types; personality, strengths, challenges, career, relationships, talents, abilities, purpose for categories)
- Required arrays properly defined
- Format hints used (format: "date" for birth_date parameter)

**Integration Ready:**
- NUMEROLOGY_TOOLS exported as list[dict] for Pipecat OpenAILLMContext.set_tools()
- Module docstring includes complete integration example with pipecat_bot.py
- Ready for Story 4.4 function handler implementation

**Validation Results:**
- Module imports successfully ✓
- NUMEROLOGY_TOOLS is a list with 4 tools ✓
- All tools have correct structure ✓
- Tool names match expected: calculate_life_path, calculate_expression_number, calculate_soul_urge_number, get_numerology_interpretation ✓
- JSON serializable (5,281 characters) ✓
- Parameters follow JSON Schema format ✓
- Enum values match database schema ✓

**Technical Details:**
- Clear, GPT-friendly descriptions that explain what each tool does, what it reveals, when to use it
- Parameter descriptions guide GPT on what to request from users
- Birth date as string with format hint (GPT-friendly) maps to Python date object in handler
- Category parameter optional to allow retrieving all categories or specific ones
- All master numbers (11, 22, 33) properly documented

**No Issues or Technical Debt:**
- Clean implementation, no shortcuts
- Follows project patterns from pipecat_bot.py
- Ready for immediate use in Story 4.4

### File List

**New Files Created:**
- `backend/src/voice_pipeline/numerology_functions.py` - OpenAI function calling definitions (218 lines, 4 tool definitions, 5,281 character JSON)

**Modified Files:**
- None (this story only creates new files)
