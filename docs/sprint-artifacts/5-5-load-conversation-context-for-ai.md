# Story 5.5: Load Conversation Context for AI

Status: ready-for-dev

## Story

As a backend developer,
I want the AI to load previous conversation summaries when starting,
So that it can reference past discussions.

## Acceptance Criteria

1. When bot starts, load recent 5 conversations for user
2. Create summary of each past conversation
3. Include summaries in system prompt context
4. AI can reference "As we discussed last time..."
5. Context doesn't exceed token limits (summarize if needed)
6. Cached in Redis for fast access

## Tasks / Subtasks

- [ ] Task 1: Implement Conversation History Retrieval (AC: #1-2)
  - [ ] Create function `get_recent_conversations()` in conversation service
  - [ ] Query database for user's last 5 completed conversations
  - [ ] Extract key information: main_topic, key_insights, numbers_discussed
  - [ ] Generate concise summary (max 100 tokens per conversation)
  - [ ] Return list of conversation summaries

- [ ] Task 2: Integrate Context into Voice Pipeline (AC: #3-4)
  - [ ] Update `pipecat_bot.py` to call `get_recent_conversations()` before bot starts
  - [ ] Format conversation summaries for system prompt
  - [ ] Update `get_numerology_system_prompt()` to accept conversation history parameter
  - [ ] Inject conversation context into system prompt: "Previous conversations: ..."
  - [ ] Ensure AI can reference past discussions naturally

- [ ] Task 3: Token Limit Management (AC: #5)
  - [ ] Calculate token count for conversation context using tiktoken
  - [ ] Implement summarization if context exceeds 500 tokens
  - [ ] Prioritize most recent conversations if needed
  - [ ] Ensure total system prompt stays under model limits (GPT-5-mini: 128k context)

- [ ] Task 4: Redis Caching Layer (AC: #6)
  - [ ] Cache formatted conversation context in Redis with key: `context:{user_id}`
  - [ ] Set TTL: 30 minutes (conversations don't change frequently)
  - [ ] Implement cache-aside pattern: check cache → DB → store cache
  - [ ] Invalidate cache when new conversation completes

- [ ] Task 5: Testing and Validation
  - [ ] Write unit tests for `get_recent_conversations()` function
  - [ ] Write unit tests for context formatting logic
  - [ ] Test with users having 0, 1, 3, 5, and 10+ conversations
  - [ ] Verify token counting accuracy
  - [ ] Test Redis caching (hit/miss scenarios)
  - [ ] Manual end-to-end test: Start conversation → AI references past discussion
  - [ ] Verify AI can say "As we discussed last time..."

## Dev Notes

### Architecture Patterns and Constraints

**Voice Pipeline Architecture:**
- Pipecat-ai orchestrates the voice conversation pipeline [Source: docs/architecture.md#Voice-Pipeline-Integration]
- Voice pipeline components: Deepgram (STT) → OpenAI GPT-5-mini (LLM) → ElevenLabs (TTS) via Daily.co WebRTC
- System prompt is set before bot starts, passed to `OpenAILLMContext` [Source: docs/architecture.md#Pattern-Pipecat-Bot-Lifecycle]
- Bot initialization happens in `create_conversation_bot()` function

**Conversation Data Model:**
- Conversation table stores: id, user_id, started_at, ended_at, main_topic, key_insights, numbers_discussed
- ConversationMessage table stores full transcript: conversation_id, role, content, timestamp
- Both available for context retrieval [Source: docs/architecture.md#Database-Models]

**Caching Strategy:**
- Redis used for caching expensive operations with check-cache → compute → store pattern
- Conversation context is expensive (DB query + formatting + token counting)
- Cache key format: `context:{user_id}` with 30-minute TTL [Source: docs/architecture.md#Caching-Patterns]

**Token Management:**
- Azure OpenAI GPT-5-mini supports 128k context window
- Use tiktoken library to count tokens accurately
- Reserve 80% for conversation, 20% for system prompt (guideline)
- Summarize older conversations if exceeding limits

### Project Structure Notes

**Backend File Locations:**
- Voice pipeline: `apps/api/app/voice_pipeline/pipecat_bot.py` - main bot setup
- System prompts: `apps/api/app/voice_pipeline/system_prompts.py` - prompt templates
- Conversation service: `apps/api/app/services/conversation_service.py` - business logic
- Redis client: `apps/api/app/core/redis.py` - caching utilities
- Models: `apps/api/app/models/conversation.py` - database schema

**Naming Conventions:**
- Python functions: `snake_case` (get_recent_conversations, format_conversation_history)
- Redis keys: `namespace:identifier` (context:user_123)
- Database queries: SQLModel ORM (no raw SQL)

**Dependencies:**
- `tiktoken`: Token counting for OpenAI models (already in pipecat deps)
- `redis`: Already configured for caching
- `sqlmodel`: ORM for database queries

### Learnings from Previous Story

**From Story 5.4 (Conversation Detail View - Status: done)**

- **Message Structure**: Conversation messages have `role`, `content`, `timestamp` fields - available for context extraction
- **API Service Pattern**: Used `fetchConversationDetail(id)` to get full conversation - similar pattern needed for backend
- **Date Formatting**: Frontend uses date-fns for display - backend should return ISO 8601 timestamps
- **Design System**: Frontend follows Celestial Gold colors - not relevant for backend story

**Key Takeaway**: Conversation data model is well-established with messages stored properly. This story focuses on backend logic to retrieve and format that data for AI context.

**From Story 5.2 (Get Conversation History Endpoint - Completed Earlier)**

- Endpoint: GET `/api/v1/conversations` returns list of conversations
- Response includes: id, started_at, ended_at, duration_seconds, main_topic, key_insights, numbers_discussed
- Authentication required (JWT token)
- Pagination supported (page, limit)

**Key Takeaway**: Backend already has conversation retrieval logic. Can reuse query patterns for getting recent conversations.

**From Story 5.1 (Conversation Message Model & Saving - Completed Earlier)**

- ConversationMessage model saves full transcript during voice conversations
- Messages linked to conversation via conversation_id foreign key
- Role field distinguishes user vs AI messages
- Content field stores message text
- Timestamp tracks when message was sent

**Key Takeaway**: Full conversation transcript is available. Can build summaries from main_topic, key_insights, or by analyzing message content.

[Source: docs/sprint-artifacts/5-4-conversation-detail-view.md#Dev-Agent-Record]

### Implementation Guidance

**Step 1: Conversation History Retrieval Function**

```python
# File: apps/api/app/services/conversation_service.py (extend existing)

async def get_recent_conversations(user_id: UUID, limit: int = 5) -> List[dict]:
    """
    Retrieve recent completed conversations for context.

    Returns list of conversation summaries:
    - conversation_id
    - started_at
    - main_topic
    - key_insights
    - numbers_discussed
    """
    session = get_db_session()

    # Query recent completed conversations
    conversations = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.ended_at != None)  # Only completed
        .order_by(Conversation.started_at.desc())
        .limit(limit)
    )

    results = conversations.scalars().all()

    # Format for context
    summaries = []
    for conv in results:
        summaries.append({
            "id": str(conv.id),
            "date": conv.started_at.isoformat(),
            "topic": conv.main_topic or "General discussion",
            "insights": conv.key_insights or "",
            "numbers": conv.numbers_discussed or []
        })

    return summaries
```

**Step 2: Context Formatting Function**

```python
# File: apps/api/app/voice_pipeline/system_prompts.py (extend existing)

def format_conversation_history(conversations: List[dict]) -> str:
    """
    Format conversation summaries for system prompt.

    Returns concise summary string optimized for token usage.
    """
    if not conversations:
        return ""

    context_parts = ["Previous conversations with this user:"]

    for i, conv in enumerate(conversations, 1):
        date = format_date(conv["date"])  # e.g., "Nov 23"
        topic = conv["topic"]
        insights = conv["insights"][:100] if conv["insights"] else ""  # Truncate
        numbers = ", ".join(map(str, conv["numbers"][:3]))  # Max 3 numbers

        context_parts.append(
            f"{i}. {date}: {topic}. "
            f"Discussed numbers: {numbers}. "
            f"Key insight: {insights}"
        )

    return "\n".join(context_parts)
```

**Step 3: Token Counting & Limit Management**

```python
# File: apps/api/app/voice_pipeline/system_prompts.py

import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def format_conversation_history(conversations: List[dict], max_tokens: int = 500) -> str:
    """
    Format conversations with token limit.

    If exceeds max_tokens, reduce number of conversations or summarize further.
    """
    context = format_conversation_history_full(conversations)

    token_count = count_tokens(context)

    if token_count <= max_tokens:
        return context

    # Reduce conversations (keep most recent)
    for reduced_count in range(len(conversations) - 1, 0, -1):
        context = format_conversation_history_full(conversations[:reduced_count])
        if count_tokens(context) <= max_tokens:
            return context

    # If still too long, return minimal context
    return f"User has {len(conversations)} previous conversations about numerology."
```

**Step 4: Redis Caching Integration**

```python
# File: apps/api/app/services/conversation_service.py

import json
from app.core.redis import get_redis_client

async def get_conversation_context_cached(user_id: UUID) -> str:
    """
    Get conversation context with Redis caching.

    Cache key: context:{user_id}
    TTL: 30 minutes
    """
    redis = get_redis_client()
    cache_key = f"context:{user_id}"

    # Check cache
    cached = await redis.get(cache_key)
    if cached:
        return cached.decode('utf-8')

    # Compute if miss
    conversations = await get_recent_conversations(user_id, limit=5)
    context = format_conversation_history(conversations, max_tokens=500)

    # Store in cache
    await redis.set(cache_key, context, ex=1800)  # 30 minutes

    return context
```

**Step 5: Update Pipecat Bot Initialization**

```python
# File: apps/api/app/voice_pipeline/pipecat_bot.py (update existing)

async def create_conversation_bot(conversation_id: str, user_id: str):
    # ... existing code ...

    # Load user context (BEFORE building system prompt)
    user = await db.get_user(user_id)
    profile = await numerology_service.get_full_profile(user)

    # NEW: Load conversation history context
    conversation_context = await get_conversation_context_cached(user_id)

    # Build system prompt WITH context
    system_prompt = get_numerology_system_prompt(
        user=user,
        profile=profile,
        conversation_history=conversation_context  # NEW parameter
    )

    # ... rest of pipeline setup ...
```

**Step 6: Update System Prompt Template**

```python
# File: apps/api/app/voice_pipeline/system_prompts.py (update existing)

def get_numerology_system_prompt(
    user: User,
    profile: NumerologyProfile,
    conversation_history: str = ""  # NEW parameter
) -> str:
    """
    Generate system prompt with user context and conversation history.
    """
    base_prompt = f"""
You are a knowledgeable numerologist assistant for {user.full_name}.

User Profile:
- Life Path Number: {profile.life_path_number}
- Expression Number: {profile.expression_number}
- Soul Urge Number: {profile.soul_urge_number}
- Birthday Number: {profile.birthday_number}
- Personal Year: {profile.personal_year}

{conversation_history}

You can reference previous conversations naturally, e.g., "As we discussed last time..."
Provide insights based on their unique numerology profile and past discussions.
"""

    return base_prompt.strip()
```

### Testing Strategy

**Unit Tests:**

```python
# File: apps/api/tests/services/test_conversation_service.py

async def test_get_recent_conversations_returns_latest_5():
    # Create 10 conversations for user
    # Assert function returns 5 most recent
    pass

async def test_get_recent_conversations_excludes_active():
    # Create conversations with ended_at = None
    # Assert only completed conversations returned
    pass

async def test_format_conversation_history_within_token_limit():
    # Create conversations with long insights
    # Assert formatted context under 500 tokens
    pass

async def test_redis_cache_hit():
    # Call get_conversation_context_cached() twice
    # Assert second call uses cache (no DB query)
    pass

async def test_redis_cache_invalidation():
    # Cache context, complete new conversation
    # Assert cache invalidated, new context generated
    pass
```

**Integration Tests:**

```python
# File: apps/api/tests/voice_pipeline/test_pipecat_bot.py

async def test_bot_includes_conversation_context():
    # Create user with 3 past conversations
    # Start new bot
    # Assert system prompt includes "Previous conversations:"
    pass

async def test_bot_handles_no_previous_conversations():
    # Create new user with 0 conversations
    # Start bot
    # Assert system prompt generated without errors
    pass
```

**Manual End-to-End Test:**

1. Create test user with 3 completed conversations about different numerology topics
2. Start new voice conversation via `/api/v1/conversations/start`
3. Say: "What did we talk about last time?"
4. Verify AI references previous conversation accurately
5. Say: "What's my life path number?" (should already know from context)
6. Verify AI responds without recalculating (uses profile + context)

### References

- Epic 5 Story 5: [Source: docs/epics.md#Story-5-5-Load-Conversation-Context-for-AI]
- Voice Pipeline Architecture: [Source: docs/architecture.md#Voice-Pipeline-Integration]
- Pipecat Bot Lifecycle Pattern: [Source: docs/architecture.md#Pattern-Pipecat-Bot-Lifecycle]
- Caching Pattern: [Source: docs/architecture.md#Caching-Patterns]
- Conversation Data Models: [Source: docs/architecture.md#Database-Models]
- System Prompt Setup: [Source: docs/architecture.md#Pattern-Numerology-Function-Calling]
- Token Management: Azure OpenAI GPT-5-mini documentation
- Story 5.2 Backend API: [Source: docs/sprint-artifacts/5-2-get-conversation-history-endpoint.md]
- Story 5.4 Message Structure: [Source: docs/sprint-artifacts/5-4-conversation-detail-view.md#API-Integration]

## Dev Agent Record

### Context Reference

- **Story Context**: [5-5-load-conversation-context-for-ai.context.xml](./5-5-load-conversation-context-for-ai.context.xml) - Generated 2025-11-23
  - Documentation artifacts (Epic 5 requirements, Architecture voice pipeline & caching patterns, Database models, Story 5.4 patterns)
  - Code artifacts (Voice pipeline bot, System prompts, Conversation service, Redis client, Conversation model)
  - Interfaces (Async functions for context retrieval, formatting, caching; System prompt builder signature update)
  - Development constraints (Voice pipeline integration, Token management, Redis caching, Database queries, Python naming)
  - Test validation approach (Unit tests for service functions, Integration tests for bot initialization, Manual end-to-end testing)

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-23: Story created from Epic 5 requirements by create-story workflow
  - Extracted acceptance criteria from epics.md
  - Analyzed previous story (5.4) for learnings and patterns
  - Referenced architecture patterns for voice pipeline and caching
  - Created comprehensive implementation guidance with code examples
  - Defined 5 tasks with clear subtasks mapped to acceptance criteria
  - Added testing strategy (unit, integration, manual end-to-end)
  - Status: backlog → drafted
