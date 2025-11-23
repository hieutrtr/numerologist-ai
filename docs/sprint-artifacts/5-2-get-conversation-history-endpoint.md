# Story 5.2: Get Conversation History Endpoint

Status: ready-for-dev

## Story

As a user,
I want to view my past conversations,
so that I can see what we discussed before.

## Acceptance Criteria

1. Endpoint: `GET /api/v1/conversations` (requires auth)
2. Returns list of user's conversations with summary
3. Each conversation shows: id, started_at, ended_at, duration, main_topic
4. Paginated (20 per page)
5. Ordered by most recent first
6. Endpoint: `GET /api/v1/conversations/{id}` returns full conversation with all messages
7. Can test with Postman - see conversation list

## Tasks / Subtasks

- [ ] Task 1: Implement GET /conversations endpoint (AC: #1-5)
  - [ ] Create ConversationListResponse schema with required fields
  - [ ] Implement list_conversations endpoint with authentication
  - [ ] Add pagination parameters (page, limit)
  - [ ] Query conversations filtered by user_id
  - [ ] Order by started_at descending
  - [ ] Test with Postman to verify pagination and auth

- [ ] Task 2: Implement GET /conversations/{id} endpoint (AC: #6)
  - [ ] Create ConversationDetailResponse schema including messages
  - [ ] Implement get_conversation endpoint with authentication
  - [ ] Verify user owns the conversation before returning
  - [ ] Include all messages ordered by timestamp
  - [ ] Handle 404 for non-existent conversations
  - [ ] Test with Postman to verify full conversation retrieval

- [ ] Task 3: Write unit and integration tests (AC: #7)
  - [ ] Test list endpoint with multiple conversations
  - [ ] Test pagination behavior (page 1, page 2, limits)
  - [ ] Test ordering (most recent first)
  - [ ] Test authentication requirement
  - [ ] Test authorization (user can't see other user's conversations)
  - [ ] Test detail endpoint with messages
  - [ ] Test 404 handling for non-existent conversation

## Dev Notes

### Architecture Patterns and Constraints

**From Architecture Document:**
- Use FastAPI router pattern for API endpoints [Source: docs/architecture.md#API-Endpoints]
- Implement proper pagination using OFFSET/LIMIT pattern [Source: docs/architecture.md#Database-Performance]
- Follow API response wrapper pattern (APIResponse with success/error structure) [Source: docs/architecture.md#API-Response-Patterns]
- Use SQLModel for database queries with proper indexing [Source: docs/architecture.md#Database-Models]
- Implement authentication using JWT token with `Depends(get_current_user)` [Source: docs/architecture.md#Authentication-Authorization]
- All endpoints return consistent JSON structure with success/error fields [Source: docs/architecture.md#API-Contracts]

**Database Query Optimization:**
- Index on `user_id` and `started_at` for fast conversation retrieval [Source: docs/architecture.md#Database-Indexes]
- Use eager loading for relationships to avoid N+1 queries
- Implement pagination to handle large conversation histories efficiently

**API Security:**
- Verify user ownership before returning conversation data
- Use proper HTTP status codes (200, 404, 403)
- Log access attempts for security auditing

### Project Structure Notes

**File Locations:**
- Endpoint: `backend/src/api/v1/endpoints/conversations.py` (extend existing router)
- Schemas: Add to existing schemas in conversations.py or create `backend/src/schemas/conversation.py`
- Tests: `backend/tests/api/test_conversations.py`

**Naming Conventions:**
- Endpoint paths: `/api/v1/conversations` (plural, kebab-case) [Source: docs/architecture.md#Naming-Conventions]
- Response models: `ConversationListResponse`, `ConversationDetailResponse` (PascalCase)
- Functions: `list_conversations`, `get_conversation` (snake_case)

### Learnings from Previous Story

**From Story 5.1 (Conversation Message Model & Saving):**

- **ConversationMessage Model Created**: Available at `backend/src/models/conversation_message.py` - use this model to fetch messages
- **Field Name Important**: Use `message_metadata` NOT `metadata` (renamed to avoid SQLAlchemy reserved word conflict)
- **GET Messages Endpoint Already Exists**: `GET /conversations/{id}/messages` endpoint was created in Story 5.1 at backend/src/api/v1/endpoints/conversations.py:316-472
  - This endpoint already returns paginated messages for a conversation
  - Can reference this implementation pattern for the list endpoint
  - Note: This endpoint has pagination, authentication, and proper response schemas
- **Response Schema Pattern**: MessageResponse and ConversationMessagesResponse schemas exist as reference (lines 33-52)
- **Authorization Pattern**: Story 5.1 validates conversation ownership at lines 404-412 - follow same pattern
- **Database Migration Pending**: Migration created but not applied yet (requires DB to be running with `alembic upgrade head`)
- **Test File Issues**: Previous story's tests have import path errors (`backend.src` should be `src`) - avoid this mistake

**Files Created in Story 5.1:**
- `backend/src/models/conversation_message.py` - ConversationMessage model (use for fetching messages)
- `backend/alembic/versions/829cdee8a29a_*.py` - Database migration for conversation_message table
- GET /conversations/{id}/messages endpoint - Reference implementation for this story

**Key Implementation Pattern to Reuse:**
```python
# From Story 5.1 - Authorization check pattern (lines 404-412)
conversation = session.exec(
    select(Conversation).where(Conversation.id == conversation_id)
).first()
if not conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")
if conversation.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
```

**Technical Debt from Story 5.1 to Consider:**
- Review findings mentioned unused imports and TYPE_CHECKING issues - keep code clean
- COUNT query optimization needed (`func.count()` instead of `len(.all())`) - apply this optimization
- Integration tests were incomplete - ensure this story includes comprehensive tests

[Source: stories/5-1-conversation-message-model-saving.md#Dev-Agent-Record]
[Source: stories/5-1-conversation-message-model-saving.md#Senior-Developer-Review]

### Implementation Guidance

**List Conversations Endpoint:**
```python
@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Retrieve paginated list of user's conversations.
    Returns conversations ordered by most recent first.
    """
    offset = (page - 1) * limit

    # Query conversations
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.started_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    # Count total for pagination metadata
    total = session.exec(
        select(func.count())
        .select_from(Conversation)
        .where(Conversation.user_id == current_user.id)
    ).one()

    return ConversationListResponse(
        conversations=conversations,
        page=page,
        limit=limit,
        total=total
    )
```

**Detail Conversation Endpoint:**
```python
@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve full conversation with all messages.
    Requires user to own the conversation.
    """
    # Verify conversation exists and user owns it
    conversation = session.exec(
        select(Conversation).where(Conversation.id == conversation_id)
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Fetch messages ordered by timestamp
    messages = session.exec(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.timestamp.asc())
    ).all()

    return ConversationDetailResponse(
        conversation=conversation,
        messages=messages
    )
```

### Testing Strategy

**Test Coverage Required:**
1. **Authentication Tests**: Verify endpoints require valid JWT token
2. **Authorization Tests**: Verify users can only access their own conversations
3. **Pagination Tests**: Test page boundaries, limit enforcement, total count
4. **Ordering Tests**: Verify most recent conversations appear first
5. **Edge Cases**: Empty conversation list, single conversation, conversation not found
6. **Data Integrity**: Verify all fields present in response (id, started_at, ended_at, etc.)

**Test Database Setup:**
- Use test fixtures to create users and conversations
- Create multiple conversations with different timestamps to test ordering
- Test with conversations from different users to verify authorization

### References

- Epic 5 Requirements: [Source: docs/epics.md#Story-5-2]
- Architecture API Patterns: [Source: docs/architecture.md#API-Contracts]
- Conversation Model: [Source: backend/src/models/conversation.py]
- Previous Story Implementation: [Source: stories/5-1-conversation-message-model-saving.md]
- API Response Pattern: [Source: docs/architecture.md#API-Response-Patterns]
- Database Performance: [Source: docs/architecture.md#Performance-Considerations]

## Dev Agent Record

### Context Reference

- **Story Context**: [5-2-get-conversation-history-endpoint.context.xml](./5-2-get-conversation-history-endpoint.context.xml) - Generated 2025-11-23
  - Documentation artifacts (Architecture API patterns, Epic 5 requirements, UX design)
  - Code artifacts (Conversation model, ConversationMessage model, existing endpoints with pagination patterns)
  - Interfaces (REST endpoints, Pydantic response schemas)
  - Development constraints (FastAPI patterns, authentication, authorization, pagination)
  - Test validation approach (pytest patterns, API testing, authorization testing)

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-23: Story created from Epic 5 requirements by create-story workflow
