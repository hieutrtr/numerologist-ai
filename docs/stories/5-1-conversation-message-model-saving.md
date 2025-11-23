# Story 5.1: Conversation Message Model & Saving

Status: ready-for-dev

## Story

As a backend developer,
I want to save conversation messages during the session,
so that we have a record of what was discussed.

## Acceptance Criteria

1. `ConversationMessage` model created in `backend/src/models/conversation_message.py`
2. Fields: `id`, `conversation_id`, `role` (user/assistant), `content`, `timestamp`, `metadata` (JSON)
3. Alembic migration creates table with proper foreign keys and indexes
4. During conversation, each message saved to database asynchronously
5. Messages linked to Conversation via foreign key relationship
6. Can query messages for a conversation ordered by timestamp
7. Non-blocking save operations (doesn't affect voice latency)
8. Both user and assistant messages captured with accurate timestamps

## Tasks / Subtasks

- [ ] Task 1: Create ConversationMessage model (AC: #1-2)
  - [ ] Create model file with SQLModel structure
  - [ ] Define fields with proper types and constraints
  - [ ] Add foreign key relationship to Conversation model
  - [ ] Update Conversation model with back-reference

- [ ] Task 2: Generate and run database migration (AC: #3)
  - [ ] Generate Alembic migration with `alembic revision --autogenerate`
  - [ ] Review migration file for correctness
  - [ ] Apply migration with `alembic upgrade head`
  - [ ] Verify table structure in PostgreSQL

- [ ] Task 3: Integrate message saving into voice pipeline (AC: #4, #7-8)
  - [ ] Hook into pipecat bot message events
  - [ ] Implement async save_user_message handler
  - [ ] Implement async save_assistant_message handler
  - [ ] Ensure non-blocking database operations
  - [ ] Handle save errors gracefully without breaking conversation

- [ ] Task 4: Create service method for querying messages (AC: #5-6)
  - [ ] Add get_conversation_messages method to conversation service
  - [ ] Implement ordering by timestamp
  - [ ] Add pagination support for large conversations
  - [ ] Create response schema for message data

- [ ] Task 5: Write integration tests
  - [ ] Test model creation and relationships
  - [ ] Test message saving during conversation
  - [ ] Test querying messages with ordering
  - [ ] Test error handling for database failures
  - [ ] Verify non-blocking operation doesn't impact latency

## Dev Notes

### Architecture Patterns and Constraints

**From Architecture Document:**
- Use SQLModel for ORM operations (consistent with existing models)
- PostgreSQL as primary database with proper indexing
- Async operations throughout for performance
- Follow existing naming conventions: snake_case for tables/columns
- Foreign key pattern: `{table}_id` (e.g., `conversation_id`)
- Timestamps use `datetime.utcnow()` pattern

**Database Considerations:**
- Index on `conversation_id` for fast message retrieval
- Consider composite index on `(conversation_id, timestamp)` for ordered queries
- Text field for content (no length limit on conversation messages)
- JSON field for metadata allows flexible additional data storage

**Voice Pipeline Integration:**
- Must not block voice pipeline (use background tasks or async operations)
- Hook into existing Pipecat event handlers
- Maintain <3 second voice latency requirement
- Database saves should be fire-and-forget during conversation

### Project Structure Notes

**File Locations:**
- Model: `backend/src/models/conversation_message.py`
- Migration: `backend/alembic/versions/` (auto-generated)
- Integration point: `backend/src/voice_pipeline/pipecat_bot.py`
- Tests: `backend/tests/models/test_conversation_message.py`

**Naming Conventions:**
- Table name: `conversation_message` (singular, snake_case)
- Model class: `ConversationMessage` (PascalCase)
- Foreign key: `conversation_id` (references `conversation.id`)

### Learnings from Previous Story

**From Story 4-5 (Numerology System Prompt):**

- **Vietnamese Prompt Integration**: System prompts module created at `backend/src/voice_pipeline/system_prompts.py` - can reference for message context enrichment
- **Pipecat Bot Updates**: `run_bot()` function now accepts optional User parameter - ensure message saving works with this updated signature
- **Event Handling Pattern**: Previous story showed deferred imports to avoid circular dependencies - apply same pattern if needed
- **Testing Approach**: Comprehensive test suite with 35+ test cases created - follow similar thorough testing pattern
- **Non-blocking Operations**: Vietnamese prompt generation uses async patterns - apply same for message saving

**Key Integration Points to Consider:**
- The pipecat_bot.py was modified (~30 lines) in story 4-5
- User object flows through conversation pipeline
- System already handles async operations well
- Database session management patterns established

[Source: stories/4-5-numerology-system-prompt.md#Dev-Agent-Record]

### Implementation Example

```python
# backend/src/models/conversation_message.py
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Text, JSON
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional

class ConversationMessage(SQLModel, table=True):
    __tablename__ = "conversation_message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    role: str = Field(sa_column=Column(Enum("user", "assistant", name="message_role")))
    content: str = Field(sa_column=Column(Text))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Relationship
    conversation: "Conversation" = Relationship(back_populates="messages")
```

```python
# Integration in pipecat_bot.py
from src.models.conversation_message import ConversationMessage
from src.core.database import get_async_session

# Hook into message events (non-blocking):
@transport.event_handler("on_user_message")
async def save_user_message(message: str):
    asyncio.create_task(
        _save_message_async(conversation_id, "user", message)
    )

async def _save_message_async(conv_id: UUID, role: str, content: str):
    async with get_async_session() as session:
        msg = ConversationMessage(
            conversation_id=conv_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        session.add(msg)
        await session.commit()
```

### Testing Strategy

1. **Unit Tests**: Model validation, field constraints
2. **Integration Tests**: Database operations, foreign keys
3. **Performance Tests**: Verify non-blocking saves don't impact latency
4. **End-to-End Tests**: Full conversation flow with message persistence

### References

- Architecture Document: [Source: docs/architecture.md#Database-Models]
- Epic 5 Requirements: [Source: docs/epics.md#Story-5-1]
- Previous Story Pattern: [Source: stories/4-5-numerology-system-prompt.md#Pipecat-Bot-Integration]
- Sprint Status: [Source: docs/sprint-status.yaml#L104]

## Dev Agent Record

### Context Reference

- **Story Context**: [5-1-conversation-message-model-saving.context.xml](./5-1-conversation-message-model-saving.context.xml) - Generated 2025-11-22
  - Documentation artifacts (Architecture patterns, Epic 5 requirements)
  - Code artifacts (Conversation model, Pipecat bot, Database patterns, API endpoints)
  - Interfaces (Model relationships, Event handlers, REST endpoints)
  - Development constraints (Async patterns, Non-blocking operations, Voice latency requirements)
  - Test validation approach (pytest-asyncio patterns, latency benchmarking, error scenarios)

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-22: Story created from Epic 5 requirements by create-story workflow