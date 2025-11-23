# Test Design: Story 5.1 - Conversation Message Model & Saving

**Story ID**: 5.1
**Epic**: 5 - Conversation Management
**Test Architect**: Murat (Master Test Architect)
**Date**: 2025-11-23
**Status**: Ready for Implementation

---

## Executive Summary

This test design covers Story 5.1: Conversation Message Model & Saving, which introduces persistent message storage for voice conversations. The design includes **22 test scenarios** across 4 test levels (Unit, Integration, API, E2E) with **8 identified risks**, including 2 high-priority risks (score ≥6) requiring explicit mitigation.

**Critical Focus Areas:**
- **Security**: Authorization checks to prevent privacy leaks (R-002, score 6)
- **Performance**: Voice latency must remain <3s with active message saving (R-001, score 6)
- **Data Integrity**: Foreign key constraints and message ordering (R-004, R-007)
- **Operational Resilience**: Graceful error handling for database failures (R-003, R-006)

**Gate Decision Prerequisites:**
- P0 tests must pass (5 scenarios): Migration, FK enforcement, Authorization, Voice latency
- High-priority risks (R-001, R-002) must be validated through testing
- No critical blockers (score=9) identified

---

## Story Context

### Story Overview

**User Story:**
As a system, I need to persist conversation messages (user and assistant) to the database so that users can review their conversation history and the AI can maintain context across sessions.

**Acceptance Criteria:**
1. `ConversationMessage` model created in `backend/src/models/conversation_message.py`
2. Fields: `id` (UUID), `conversation_id` (FK), `role` (Enum: user/assistant), `content` (str), `timestamp` (datetime), `metadata` (JSON)
3. Alembic migration creates table with foreign keys (→conversation) and indexes (conversation_id, timestamp)
4. During voice conversation, each message saved to database asynchronously (non-blocking)
5. Messages linked to `Conversation` via foreign key relationship
6. Can query messages for a conversation via API: `GET /conversations/{id}/messages` (ordered by timestamp DESC, paginated)
7. Save operations are non-blocking and don't impact voice latency (<3s requirement)
8. Both user messages (transcribed speech) and assistant messages (AI responses) captured with accurate timestamps

### Architecture Context

**Relevant Components:**
- **Models**: `backend/app/models/conversation_message.py` (new), `conversation.py` (existing)
- **API Endpoint**: `GET /api/v1/conversations/{id}/messages` (new)
- **Voice Pipeline**: `backend/app/voice_pipeline/pipecat_bot.py` (modified for async message saving)
- **Database**: PostgreSQL with SQLModel ORM
- **Performance Target**: Voice latency <3s end-to-end (NFR-P1)

**Constraints:**
- Must use async patterns to avoid blocking voice pipeline
- SQLModel ORM for all database operations (no raw SQL)
- JWT authentication required for all API endpoints
- Foreign key relationships must maintain referential integrity
- Database migrations must be reversible (alembic downgrade)

**Integration Points:**
- Voice pipeline (Pipecat bot) → `ConversationMessage.create()` after each STT/LLM/TTS event
- API endpoint → Database query with user authorization check
- `Conversation` model → `ConversationMessage` model (one-to-many relationship)

---

## Risk Assessment

### Risk Scoring Methodology

**Probability Scale:**
- 1 = Unlikely (standard implementation, low uncertainty)
- 2 = Possible (edge cases or partial unknowns)
- 3 = Likely (known issues, new integrations, high ambiguity)

**Impact Scale:**
- 1 = Minor (cosmetic issues or easy workarounds)
- 2 = Degraded (partial feature loss or manual workaround)
- 3 = Critical (blockers, data/security/regulatory exposure)

**Risk Score**: Probability × Impact (1-9)

**Action Thresholds:**
- 1-3: DOCUMENT (awareness only)
- 4-5: MONITOR (watch closely, plan mitigations)
- 6-8: MITIGATE (CONCERNS at gate until resolved)
- 9: BLOCK (automatic FAIL until resolved or waived)

---

### High-Priority Risks (Score ≥6) - Require Mitigation

#### R-001: Voice Latency Impact from Database Saves
- **Category**: PERF (Performance)
- **Probability**: 2 (Possible)
- **Impact**: 3 (Critical)
- **Score**: **6** (MITIGATE)
- **Description**: Async message saving might still impact voice pipeline latency if database operations block or cause contention. NFR-P1 requires <3s end-to-end latency (STT → LLM → TTS).
- **Evidence**:
  - PRD NFR-P1: Voice latency must remain <3 seconds
  - Story AC#7: "Non-blocking save operations"
  - Architecture uses async/await patterns but needs load testing validation
- **Mitigation Plan**:
  - **Test Coverage**: 5.1-E2E-002 (measure actual latency during conversation with active saving)
  - **Test Coverage**: 5.1-INT-007 (benchmark async dispatch time <50ms)
  - **Test Coverage**: 5.1-INT-011 (measure p95 dispatch time under load)
  - **Implementation**: Use background tasks (asyncio.create_task) for database saves
  - **Monitoring**: Add latency tracking for save operations in production logs
- **Test Priority**: P0 (Critical - blocks NFR-P1 compliance)

---

#### R-002: Conversation History Privacy Leak
- **Category**: SEC (Security)
- **Probability**: 2 (Possible)
- **Impact**: 3 (Critical)
- **Score**: **6** (MITIGATE)
- **Description**: `GET /conversations/{id}/messages` endpoint might return messages from conversations the authenticated user doesn't own, exposing private conversation data.
- **Evidence**:
  - PRD NFR-S4: GDPR compliance required (privacy-first)
  - Architecture pattern: JWT auth required but authorization checks are implementation responsibility
  - Common vulnerability: authentication ≠ authorization
- **Mitigation Plan**:
  - **Test Coverage**: 5.1-API-003 (verify 403 Forbidden when User B queries User A's conversation)
  - **Implementation**: Add authorization check in endpoint: `if conversation.user_id != current_user.id: raise HTTPException(403)`
  - **Code Review**: Ensure all conversation-related endpoints perform ownership check
- **Test Priority**: P0 (Critical - security violation, GDPR breach)

---

### Medium-Priority Risks (Score 4-5) - Monitor

#### R-003: Database Connection Failures During Conversation
- **Category**: TECH (Technical)
- **Probability**: 2 (Possible)
- **Impact**: 2 (Degraded)
- **Score**: **4** (MONITOR)
- **Description**: Message saving fails when PostgreSQL connection unavailable (network issue, connection pool exhaustion). If not handled, could crash voice pipeline.
- **Mitigation**:
  - **Test Coverage**: 5.1-INT-008 (simulate DB down, verify graceful error handling)
  - **Implementation**: Wrap save operations in try/except, log errors but don't raise to pipeline
  - **Monitoring**: Alert on elevated save failure rates

#### R-004: Race Conditions in Message Order
- **Category**: DATA (Data Integrity)
- **Probability**: 2 (Possible)
- **Impact**: 2 (Degraded)
- **Score**: **4** (MONITOR)
- **Description**: Concurrent async saves might cause messages to arrive in database out of chronological order, confusing users reviewing conversation history.
- **Mitigation**:
  - **Test Coverage**: 5.1-API-001 (verify messages returned in DESC timestamp order)
  - **Test Coverage**: 5.1-INT-012 (timestamp accuracy validation)
  - **Implementation**: Use database-generated timestamps (default=datetime.utcnow) and ORDER BY timestamp DESC in queries

#### R-005: Large Conversation Memory Bloat
- **Category**: PERF (Performance)
- **Probability**: 2 (Possible)
- **Impact**: 2 (Degraded)
- **Score**: **4** (MONITOR)
- **Description**: Very long conversations (>100 messages) could cause memory issues in Pipecat bot if entire context loaded into memory.
- **Mitigation**:
  - **Test Coverage**: 5.1-API-002 (verify pagination works with limit/offset)
  - **Test Coverage**: 5.1-INT-005 (verify indexes on conversation_id, timestamp)
  - **Implementation**: Pagination in API queries, context window management in Pipecat bot

#### R-006: Async Save Errors Not Logged
- **Category**: OPS (Operations)
- **Probability**: 2 (Possible)
- **Impact**: 2 (Degraded)
- **Score**: **4** (MONITOR)
- **Description**: Fire-and-forget async saves fail silently without error tracking, making message loss invisible to operations team.
- **Mitigation**:
  - **Test Coverage**: 5.1-INT-008 (verify errors logged when DB unavailable)
  - **Implementation**: Add structured logging (structlog) in error handlers
  - **Monitoring**: Track save error rates in Application Insights

---

### Low-Priority Risks (Score 1-3) - Document

#### R-007: Foreign Key Constraint Violations
- **Category**: DATA (Data Integrity)
- **Probability**: 1 (Unlikely)
- **Impact**: 2 (Degraded)
- **Score**: **2** (DOCUMENT)
- **Description**: Message references non-existent conversation_id if conversation deleted during async save (tiny race condition window).
- **Mitigation**:
  - **Test Coverage**: 5.1-INT-004, 5.1-INT-009 (verify FK constraint enforcement)
  - **Note**: Database enforces FK integrity; just need error handling in save logic

#### R-008: Message Content SQL Injection
- **Category**: SEC (Security)
- **Probability**: 1 (Unlikely)
- **Impact**: 3 (Critical)
- **Score**: **3** (MONITOR)
- **Description**: User voice transcription contains malicious SQL injection attempts that get executed against database.
- **Mitigation**:
  - **Implementation**: SQLModel ORM uses parameterized queries by design (prevents SQL injection)
  - **Verification**: Code review to ensure no raw SQL strings concatenated with user input
  - **Test Coverage**: Implicit (ORM usage), explicit testing not required unless raw SQL detected

---

### Risk Summary

| Risk ID | Category | Score | Action   | Test Priority | Coverage Count |
|---------|----------|-------|----------|---------------|----------------|
| R-001   | PERF     | 6     | MITIGATE | P0            | 3 scenarios    |
| R-002   | SEC      | 6     | MITIGATE | P0            | 1 scenario     |
| R-003   | TECH     | 4     | MONITOR  | P1            | 2 scenarios    |
| R-004   | DATA     | 4     | MONITOR  | P1            | 3 scenarios    |
| R-005   | PERF     | 4     | MONITOR  | P2            | 2 scenarios    |
| R-006   | OPS      | 4     | MONITOR  | P1            | 1 scenario     |
| R-007   | DATA     | 2     | DOCUMENT | P0            | 3 scenarios    |
| R-008   | SEC      | 3     | MONITOR  | Code Review   | Implicit       |

**Total Risks**: 8
**High-Priority (≥6)**: 2 (MITIGATE required)
**Medium-Priority (4-5)**: 4 (MONITOR closely)
**Low-Priority (1-3)**: 2 (DOCUMENT only)

---

## Test Scenarios

### Test ID Format
`{EPIC}.{STORY}-{LEVEL}-{SEQ}`

Example: `5.1-INT-001` = Epic 5, Story 1, Integration Test, Sequence 001

---

### AC#1: ConversationMessage Model Created

#### 5.1-UNIT-001: Model instantiation with valid fields
- **Test Level**: Unit
- **Priority**: P2 (Medium)
- **Risk Link**: -
- **Objective**: Verify `ConversationMessage` model instantiates correctly with all required fields
- **Preconditions**: Model class defined in `backend/app/models/conversation_message.py`
- **Test Steps**:
  1. Import `ConversationMessage` model
  2. Create instance with valid data: `id=uuid4()`, `conversation_id=uuid4()`, `role="user"`, `content="Test"`, `timestamp=datetime.utcnow()`, `metadata={}`
  3. Assert all attributes set correctly
- **Expected Result**: Model instance created without errors, attributes accessible
- **Test Data**: Valid UUID, enum value, string, datetime, empty dict

#### 5.1-INT-001: Model persists to database successfully
- **Test Level**: Integration
- **Priority**: P1 (High)
- **Risk Link**: R-003 (DB connection failures)
- **Objective**: Verify model saves to PostgreSQL test database and can be retrieved
- **Preconditions**: Test database running, Alembic migration applied
- **Test Steps**:
  1. Create test conversation fixture in database
  2. Create `ConversationMessage` instance linked to conversation
  3. Call `db.add(message)` and `db.commit()`
  4. Query database for message by ID
  5. Assert message retrieved with correct values
- **Expected Result**: Message row exists in `conversation_message` table with correct field values
- **Test Data**: Conversation fixture (id, user_id), message content "Integration test message"

---

### AC#2: Model Fields Defined Correctly

#### 5.1-UNIT-002: Field types validated
- **Test Level**: Unit
- **Priority**: P2 (Medium)
- **Risk Link**: -
- **Objective**: Verify model field types match schema (UUID, Enum, str, datetime, JSON)
- **Preconditions**: Model class defined with type annotations
- **Test Steps**:
  1. Inspect model class annotations: `ConversationMessage.__annotations__`
  2. Assert `id: UUID`, `conversation_id: UUID`, `role: Enum`, `content: str`, `timestamp: datetime`, `metadata: dict`
  3. Attempt to create model with invalid types (e.g., `role="invalid_role"`)
  4. Assert validation error raised
- **Expected Result**: Type annotations correct, invalid types rejected
- **Test Data**: Invalid role value "not_user_or_assistant", timestamp as string "2025-01-01"

#### 5.1-INT-002: Metadata JSON field serialization
- **Test Level**: Integration
- **Priority**: P2 (Medium)
- **Risk Link**: R-004 (Data integrity)
- **Objective**: Verify metadata dict serializes to JSON and deserializes correctly
- **Preconditions**: Database supports JSON column type
- **Test Steps**:
  1. Create message with complex metadata: `{'function_call': 'calculate_life_path', 'args': {'birth_date': '1990-05-15'}, 'result': 7}`
  2. Save to database
  3. Retrieve message from database
  4. Assert metadata dict matches original (nested structure intact)
- **Expected Result**: Metadata JSON serialization/deserialization preserves structure
- **Test Data**: Nested dict with function call details

---

### AC#3: Alembic Migration with Foreign Keys & Indexes

#### 5.1-INT-003: Migration runs successfully (up)
- **Test Level**: Integration
- **Priority**: P0 (Critical - BLOCKER)
- **Risk Link**: All risks (migration must succeed for story to proceed)
- **Objective**: Verify Alembic migration creates `conversation_message` table with correct schema
- **Preconditions**: Clean test database, migration file in `alembic/versions/`
- **Test Steps**:
  1. Run `alembic upgrade head`
  2. Query database schema: `SELECT * FROM information_schema.tables WHERE table_name='conversation_message'`
  3. Assert table exists
  4. Query columns: `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='conversation_message'`
  5. Assert columns match schema (id, conversation_id, role, content, timestamp, metadata)
- **Expected Result**: Migration executes without errors, table created with correct schema
- **Test Data**: Migration file `XXXX_add_conversation_message.py`

#### 5.1-INT-004: Foreign key constraint to conversation enforced
- **Test Level**: Integration
- **Priority**: P0 (Critical)
- **Risk Link**: R-007 (FK violations)
- **Objective**: Verify database enforces foreign key constraint from `conversation_message.conversation_id` → `conversation.id`
- **Preconditions**: Migration applied, no existing conversations in test DB
- **Test Steps**:
  1. Attempt to insert message with `conversation_id` that doesn't exist in `conversation` table
  2. Use raw SQL or ORM: `INSERT INTO conversation_message (id, conversation_id, ...) VALUES (...)`
  3. Assert `IntegrityError` raised (FK constraint violation)
- **Expected Result**: Database rejects insert with FK constraint error
- **Test Data**: Non-existent conversation_id (random UUID not in database)

#### 5.1-INT-005: Indexes created (conversation_id, timestamp)
- **Test Level**: Integration
- **Priority**: P1 (High)
- **Risk Link**: R-005 (Performance with large conversations)
- **Objective**: Verify migration creates indexes on `conversation_id` and `timestamp` columns for query performance
- **Preconditions**: Migration applied
- **Test Steps**:
  1. Query database indexes: `SELECT indexname, indexdef FROM pg_indexes WHERE tablename='conversation_message'`
  2. Assert index exists on `conversation_id` (for FK joins)
  3. Assert index exists on `timestamp` (for ORDER BY queries)
- **Expected Result**: Both indexes present in database schema
- **Test Data**: Database schema inspection

#### 5.1-INT-006: Migration rollback works (down)
- **Test Level**: Integration
- **Priority**: P3 (Low)
- **Risk Link**: -
- **Objective**: Verify Alembic downgrade removes `conversation_message` table cleanly
- **Preconditions**: Migration applied (table exists)
- **Test Steps**:
  1. Run `alembic downgrade -1`
  2. Query database schema
  3. Assert `conversation_message` table no longer exists
- **Expected Result**: Migration reversed without errors, table dropped
- **Test Data**: Database with migration applied

---

### AC#4: Messages Saved Asynchronously During Conversation

#### 5.1-E2E-001: Messages appear in database during active conversation
- **Test Level**: E2E
- **Priority**: P1 (High)
- **Risk Link**: R-001 (Voice latency), R-003 (DB failures)
- **Objective**: Verify messages are saved to database while conversation is ongoing (not just at end)
- **Preconditions**:
  - Staging environment with voice pipeline running
  - User authenticated
  - Daily.co room created and joined
  - Database accessible
- **Test Steps**:
  1. Start conversation via API: `POST /api/v1/conversations/start`
  2. Join Daily.co room and speak 3 test phrases: "Hello", "What is my life path number?", "Thank you"
  3. Wait for AI responses to each (conversation still active)
  4. During conversation, query database: `SELECT * FROM conversation_message WHERE conversation_id={id}`
  5. Assert at least 6 messages exist (3 user + 3 assistant)
  6. Verify messages saved incrementally (not all at once at end)
- **Expected Result**: Messages appear in database during active conversation, not queued until end
- **Test Data**: Test user, test phrases, active Daily room
- **Environment**: Staging with real Pipecat bot, Deepgram, GPT-5-mini, ElevenLabs

#### 5.1-INT-007: Async save operation completes quickly (<50ms dispatch)
- **Test Level**: Integration (Performance)
- **Priority**: P1 (High)
- **Risk Link**: R-001 (Voice latency impact)
- **Objective**: Verify async save function returns immediately (<50ms), actual DB commit happens in background
- **Preconditions**: Message save function implemented with async/await
- **Test Steps**:
  1. Create test message
  2. Measure time: `start = time.time()`
  3. Call async save function: `await save_message_async(message)`
  4. Measure time: `end = time.time()`
  5. Assert `(end - start) * 1000 < 50` milliseconds
  6. Verify function returns before DB commit completes (background task created)
- **Expected Result**: Function returns in <50ms (async dispatch), actual save happens in background
- **Test Data**: Sample message, timing measurement
- **Tool**: pytest-benchmark or manual timing

#### 5.1-INT-008: Save errors handled gracefully (DB unavailable)
- **Test Level**: Integration
- **Priority**: P1 (High)
- **Risk Link**: R-003 (DB connection failures), R-006 (Error logging)
- **Objective**: Verify database unavailability doesn't crash voice pipeline, errors logged properly
- **Preconditions**: Message save function implemented with error handling
- **Test Steps**:
  1. Mock database connection to raise `OperationalError` (DB down)
  2. Attempt to save message: `await save_message_async(message)`
  3. Assert no exception propagated to caller (error caught internally)
  4. Verify error logged to structlog: check log output for "message_save_failed" event
  5. Verify conversation can continue (pipeline not crashed)
- **Expected Result**: Error logged, exception not raised, conversation continues
- **Test Data**: Message to save, mocked DB failure
- **Assertion**: Log entry exists with error details, no exception raised

---

### AC#5: Messages Linked via Foreign Key

#### 5.1-INT-009: Cannot create message with invalid conversation_id
- **Test Level**: Integration
- **Priority**: P0 (Critical)
- **Risk Link**: R-007 (FK violations)
- **Objective**: Verify database prevents orphaned messages (FK constraint enforcement)
- **Preconditions**: Migration applied with FK constraint
- **Test Steps**:
  1. Create message with valid fields but non-existent `conversation_id` (UUID not in conversation table)
  2. Attempt to save: `db.add(message); db.commit()`
  3. Assert `IntegrityError` raised with FK constraint violation message
- **Expected Result**: Database rejects save, raises FK constraint error
- **Test Data**: Valid message fields, invalid conversation_id (random UUID)

#### 5.1-INT-010: Deleting conversation handles messages correctly
- **Test Level**: Integration
- **Priority**: P2 (Medium)
- **Risk Link**: R-007 (FK violations)
- **Objective**: Verify FK behavior when parent conversation deleted (cascade or prevent)
- **Preconditions**: Conversation with 5 messages in database
- **Test Steps**:
  1. Create conversation in database
  2. Create 5 messages linked to conversation
  3. Attempt to delete conversation: `db.delete(conversation); db.commit()`
  4. Check FK definition in migration (ON DELETE CASCADE or ON DELETE RESTRICT)
  5. If CASCADE: Assert messages also deleted
  6. If RESTRICT: Assert delete fails with FK constraint error
- **Expected Result**: Behavior matches FK constraint definition (cascade or prevent)
- **Test Data**: Conversation with 5 messages
- **Note**: Architecture decision required (cascade vs. restrict)

---

### AC#6: Query Messages for Conversation (Ordered)

#### 5.1-API-001: GET /conversations/{id}/messages returns messages ordered by timestamp DESC
- **Test Level**: API (Integration)
- **Priority**: P1 (High)
- **Risk Link**: R-004 (Message ordering)
- **Objective**: Verify API endpoint returns messages in reverse chronological order (newest first)
- **Preconditions**: Conversation with 10 messages at different timestamps in database
- **Test Steps**:
  1. Create conversation via API
  2. Create 10 messages with timestamps: t0, t1, t2, ..., t9 (1 second apart)
  3. Authenticate as conversation owner
  4. Call endpoint: `GET /api/v1/conversations/{id}/messages`
  5. Assert response array ordered: [message_t9, message_t8, ..., message_t0]
  6. Verify first message has latest timestamp, last message has earliest
- **Expected Result**: Messages returned in DESC timestamp order (newest first)
- **Test Data**: Conversation with 10 messages timestamped sequentially
- **Assertion**: `response[0].timestamp > response[1].timestamp > ... > response[9].timestamp`

#### 5.1-API-002: Pagination works (limit/offset)
- **Test Level**: API (Integration)
- **Priority**: P2 (Medium)
- **Risk Link**: R-005 (Large conversation memory)
- **Objective**: Verify API supports pagination with limit and page parameters
- **Preconditions**: Conversation with 50 messages in database
- **Test Steps**:
  1. Create conversation with 50 messages (m1, m2, ..., m50)
  2. Call endpoint with pagination: `GET /api/v1/conversations/{id}/messages?limit=20&page=2`
  3. Assert response contains 20 messages
  4. Verify messages are from page 2 (messages 21-40 in DESC order)
  5. Call with page=3, verify messages 41-50 returned (only 10, last page)
- **Expected Result**: Pagination works correctly, returns subset of messages per page
- **Test Data**: Conversation with 50 messages
- **Assertion**: Page 2 returns messages 21-40 (sorted DESC)

#### 5.1-API-003: Authorization check - user cannot query other users' conversations
- **Test Level**: API (Integration)
- **Priority**: P0 (Critical - SECURITY)
- **Risk Link**: R-002 (Privacy leak - score 6)
- **Objective**: Verify endpoint enforces authorization (user can only query their own conversations)
- **Preconditions**: Two users in database (User A, User B), conversation owned by User A
- **Test Steps**:
  1. Create User A and User B
  2. Create conversation owned by User A (conversation.user_id = User A id)
  3. Authenticate as User B (get JWT token for User B)
  4. Attempt to query User A's conversation: `GET /api/v1/conversations/{A_conversation_id}/messages` with User B's token
  5. Assert response status 403 Forbidden
  6. Assert error message: "You do not have permission to access this conversation"
- **Expected Result**: 403 Forbidden response, error message explains unauthorized access
- **Test Data**: Two users, conversation owned by User A
- **Security Validation**: CRITICAL - prevents GDPR violation

---

### AC#7: Non-Blocking Operations (Voice Latency)

#### 5.1-E2E-002: Voice latency remains <3s with message saving active
- **Test Level**: E2E (Performance)
- **Priority**: P0 (Critical - NFR-P1)
- **Risk Link**: R-001 (Voice latency - score 6)
- **Objective**: Verify voice pipeline maintains <3s latency while messages are being saved to database
- **Preconditions**:
  - Staging environment with production-like database load
  - Voice pipeline fully operational (Deepgram, GPT-5-mini, ElevenLabs, Daily.co)
  - Latency measurement instrumentation in place
- **Test Steps**:
  1. Start conversation with 20+ messages already in conversation (database writes active)
  2. Speak test phrase: "What is my life path number?"
  3. Measure latency from speech end → AI audio start
  4. Components: STT (Deepgram) + LLM (GPT-5-mini) + TTS (ElevenLabs) + DB save (async)
  5. Repeat 10 times, calculate p95 latency
  6. Assert p95 latency <3000ms
- **Expected Result**: 95th percentile latency <3 seconds (per NFR-P1)
- **Test Data**: Active conversation with continuous message saving
- **Environment**: Staging with production-equivalent DB and voice services
- **Tooling**: Daily.co analytics API or custom instrumentation for latency measurement
- **NFR Validation**: NFR-P1 (Voice latency <3s)

#### 5.1-INT-011: Measure async save dispatch time
- **Test Level**: Integration (Performance)
- **Priority**: P1 (High)
- **Risk Link**: R-001 (Voice latency)
- **Objective**: Benchmark async save function dispatch time (not full commit), ensure <50ms
- **Preconditions**: Async save function implemented
- **Test Steps**:
  1. Create 100 test messages
  2. For each message:
     - Measure time before call
     - Call `await save_message_async(message)`
     - Measure time after call returns
     - Record dispatch time (time to return, not time to DB commit)
  3. Calculate mean, p50, p95, p99 dispatch times
  4. Assert mean <50ms, p95 <100ms
- **Expected Result**: Async dispatch completes quickly, doesn't block caller
- **Test Data**: 100 sequential save operations
- **Tool**: pytest-benchmark
- **Assertion**: Mean dispatch <50ms, p95 <100ms

---

### AC#8: Both User and Assistant Messages Captured

#### 5.1-E2E-003: User message transcribed and saved with role='user'
- **Test Level**: E2E
- **Priority**: P1 (High)
- **Risk Link**: -
- **Objective**: Verify user speech is transcribed by Deepgram and saved to database with role='user'
- **Preconditions**: Active conversation, microphone access, Deepgram STT operational
- **Test Steps**:
  1. Start conversation
  2. Speak test phrase clearly: "What is my life path number?"
  3. Wait for transcription (Deepgram processing)
  4. Query database: `SELECT * FROM conversation_message WHERE conversation_id={id} AND role='user' ORDER BY timestamp DESC LIMIT 1`
  5. Assert message exists with role='user'
  6. Assert content approximately matches phrase (transcription accuracy ≥90%)
- **Expected Result**: User message saved with role='user', transcription accurate
- **Test Data**: Known test phrase, expected transcription
- **Assertion**: Message content contains "life path number" or similar (fuzzy match)

#### 5.1-E2E-004: Assistant response saved with role='assistant'
- **Test Level**: E2E
- **Priority**: P1 (High)
- **Risk Link**: -
- **Objective**: Verify AI response (GPT-5-mini output → ElevenLabs TTS) is saved to database with role='assistant'
- **Preconditions**: Active conversation, AI has generated response
- **Test Steps**:
  1. Trigger AI response (ask question or prompt)
  2. Wait for AI to speak response via ElevenLabs TTS
  3. Query database: `SELECT * FROM conversation_message WHERE conversation_id={id} AND role='assistant' ORDER BY timestamp DESC LIMIT 1`
  4. Assert message exists with role='assistant'
  5. Assert content matches AI response (contains key phrases from GPT-5-mini output)
- **Expected Result**: Assistant message saved with role='assistant', content matches AI output
- **Test Data**: AI response content (e.g., "Your Life Path number is 7")
- **Assertion**: Message content contains expected AI response phrases

#### 5.1-INT-012: Timestamp accuracy (within 1 second of message time)
- **Test Level**: Integration
- **Priority**: P2 (Medium)
- **Risk Link**: R-004 (Message ordering)
- **Objective**: Verify message timestamp accurately reflects when message was spoken/generated
- **Preconditions**: Message save function captures current time
- **Test Steps**:
  1. Capture client timestamp before save: `client_time = datetime.utcnow()`
  2. Save message: `await save_message_async(message)`
  3. Retrieve saved message from database
  4. Compare timestamps: `db_timestamp = message.timestamp`
  5. Calculate delta: `abs((client_time - db_timestamp).total_seconds())`
  6. Assert delta <1 second
- **Expected Result**: Timestamp in database within 1 second of actual message time
- **Test Data**: Message saved at known time
- **Assertion**: Time delta <1 second

---

## Test Coverage Summary

### By Priority

| Priority | Count | Scenarios |
|----------|-------|-----------|
| **P0 (Critical)** | 5 | 5.1-INT-003, 5.1-INT-004, 5.1-INT-009, 5.1-API-003, 5.1-E2E-002 |
| **P1 (High)** | 10 | 5.1-INT-001, 5.1-INT-005, 5.1-E2E-001, 5.1-INT-007, 5.1-INT-008, 5.1-API-001, 5.1-E2E-003, 5.1-E2E-004, 5.1-INT-011 |
| **P2 (Medium)** | 6 | 5.1-UNIT-001, 5.1-UNIT-002, 5.1-INT-002, 5.1-INT-010, 5.1-API-002, 5.1-INT-012 |
| **P3 (Low)** | 1 | 5.1-INT-006 |
| **Total** | **22** | - |

### By Test Level

| Level | Count | Scenarios |
|-------|-------|-----------|
| **Unit** | 2 | 5.1-UNIT-001, 5.1-UNIT-002 |
| **Integration** | 11 | 5.1-INT-001 through 5.1-INT-012 (excluding INT-011 moved to performance) |
| **API (Integration)** | 3 | 5.1-API-001, 5.1-API-002, 5.1-API-003 |
| **E2E** | 4 | 5.1-E2E-001, 5.1-E2E-002, 5.1-E2E-003, 5.1-E2E-004 |
| **Performance** | 2 | 5.1-E2E-002 (latency), 5.1-INT-011 (dispatch time) |
| **Total** | **22** | - |

### Risk Coverage Mapping

| Risk ID | Risk Name | Score | Scenarios Covering | Coverage |
|---------|-----------|-------|-------------------|----------|
| R-001 | Voice Latency Impact | 6 | 5.1-E2E-002, 5.1-INT-007, 5.1-INT-011 | ✅ 3 tests |
| R-002 | Privacy Leak | 6 | 5.1-API-003 | ✅ 1 test (CRITICAL) |
| R-003 | DB Connection Failures | 4 | 5.1-INT-001, 5.1-INT-008 | ✅ 2 tests |
| R-004 | Message Ordering | 4 | 5.1-API-001, 5.1-INT-002, 5.1-INT-012 | ✅ 3 tests |
| R-005 | Memory Bloat | 4 | 5.1-INT-005, 5.1-API-002 | ✅ 2 tests |
| R-006 | Error Logging | 4 | 5.1-INT-008 | ✅ 1 test |
| R-007 | FK Violations | 2 | 5.1-INT-004, 5.1-INT-009, 5.1-INT-010 | ✅ 3 tests |
| R-008 | SQL Injection | 3 | Code Review (SQLModel ORM usage) | ✅ Implicit |

**All identified risks have explicit test coverage or mitigation strategies.**

---

## Test Data Requirements

### Fixtures

```python
# backend/tests/fixtures/conversation_fixtures.py

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from app.models.user import User
from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage

@pytest.fixture
def sample_user(db):
    """Create test user in database"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        birth_date="1990-05-15",
        hashed_password="hashed_password_here"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def sample_conversation(db, sample_user):
    """Create test conversation linked to user"""
    conversation = Conversation(
        id=uuid4(),
        user_id=sample_user.id,
        daily_room_id="test-room-123",
        started_at=datetime.utcnow()
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

@pytest.fixture
def sample_message(sample_conversation):
    """Create test message (not yet saved)"""
    return ConversationMessage(
        id=uuid4(),
        conversation_id=sample_conversation.id,
        role="user",
        content="Test message content",
        timestamp=datetime.utcnow(),
        metadata={}
    )

@pytest.fixture
def conversation_with_messages(db, sample_conversation):
    """Create conversation with 10 messages"""
    messages = []
    base_time = datetime.utcnow()

    for i in range(10):
        message = ConversationMessage(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            timestamp=base_time + timedelta(seconds=i),
            metadata={}
        )
        db.add(message)
        messages.append(message)

    db.commit()
    return sample_conversation, messages

@pytest.fixture
def large_conversation_with_messages(db, sample_conversation):
    """Create conversation with 50 messages for pagination tests"""
    messages = []
    base_time = datetime.utcnow()

    for i in range(50):
        message = ConversationMessage(
            id=uuid4(),
            conversation_id=sample_conversation.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}",
            timestamp=base_time + timedelta(seconds=i),
            metadata={"sequence": i}
        )
        db.add(message)
        messages.append(message)

    db.commit()
    return sample_conversation, messages

@pytest.fixture
def two_users_with_conversations(db):
    """Create two users each with their own conversation (for auth tests)"""
    user_a = User(id=uuid4(), email="usera@example.com", ...)
    user_b = User(id=uuid4(), email="userb@example.com", ...)
    db.add_all([user_a, user_b])
    db.commit()

    conv_a = Conversation(id=uuid4(), user_id=user_a.id, ...)
    conv_b = Conversation(id=uuid4(), user_id=user_b.id, ...)
    db.add_all([conv_a, conv_b])
    db.commit()

    return (user_a, conv_a), (user_b, conv_b)
```

### Test Data Sets

**Valid Message Data:**
```python
valid_message_data = {
    "conversation_id": uuid4(),  # Valid FK
    "role": "user",  # Enum: 'user' or 'assistant'
    "content": "What is my life path number?",
    "timestamp": datetime.utcnow(),
    "metadata": {
        "source": "deepgram",
        "confidence": 0.95,
        "language": "en"
    }
}
```

**Invalid Data for Validation Tests:**
```python
invalid_role = "invalid_role"  # Should fail enum validation
invalid_conversation_id = uuid4()  # FK not in database
malformed_metadata = "not_a_dict"  # Should be dict/JSON
```

**Performance Test Data:**
```python
# 100 messages for dispatch time benchmarking
perf_messages = [
    ConversationMessage(
        conversation_id=conversation_id,
        role="user" if i % 2 == 0 else "assistant",
        content=f"Performance test message {i}",
        timestamp=datetime.utcnow()
    )
    for i in range(100)
]
```

---

## Test Environment & Tooling

### Test Database Setup

**PostgreSQL Test Database (Docker):**
```bash
# docker-compose.test.yml
services:
  postgres-test:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: numerologist_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

# Start test database
docker-compose -f docker-compose.test.yml up -d postgres-test

# Run migrations
export DATABASE_URL="postgresql://test_user:test_password@localhost:5433/numerologist_test"
alembic upgrade head
```

### Integration Test Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (database, API)
    e2e: End-to-end tests (full system)
    performance: Performance benchmarks
    p0: Priority 0 - Critical (smoke tests, blockers)
    p1: Priority 1 - High (core functionality)
    p2: Priority 2 - Medium (secondary features)
    p3: Priority 3 - Low (nice-to-have)
```

**conftest.py:**
```python
# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

# Test database URL
TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5433/numerologist_test"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    return create_engine(TEST_DATABASE_URL)

@pytest.fixture(scope="session")
def tables(engine):
    """Create all tables before tests, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(engine, tables):
    """Create new database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """FastAPI test client with database session override"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_db

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### E2E Test Environment

**Staging Environment Requirements:**
- Daily.co test room with API key
- Azure OpenAI GPT-5-mini staging endpoint
- Deepgram staging API key
- ElevenLabs staging API key
- PostgreSQL staging database
- Redis staging instance

**Environment Variables (.env.test):**
```bash
DATABASE_URL=postgresql://test_user:test_password@localhost:5433/numerologist_test
REDIS_URL=redis://localhost:6380
DAILY_API_KEY=test_daily_api_key
DEEPGRAM_API_KEY=test_deepgram_key
AZURE_OPENAI_KEY=test_openai_key
ELEVENLABS_API_KEY=test_elevenlabs_key
JWT_SECRET=test_jwt_secret
```

### Performance Testing Tools

**pytest-benchmark** (for dispatch time measurement):
```bash
pip install pytest-benchmark

# Run benchmark tests
pytest tests/integration/test_message_performance.py --benchmark-only
```

**Custom Latency Instrumentation:**
```python
# backend/app/utils/latency_tracker.py
import time
import structlog

logger = structlog.get_logger()

class LatencyTracker:
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        elapsed_ms = (time.time() - self.start_time) * 1000
        logger.info(
            "operation_latency",
            operation=self.operation_name,
            latency_ms=elapsed_ms
        )

# Usage in tests
with LatencyTracker("message_save_async"):
    await save_message_async(message)
```

---

## Test Execution Strategy

### Execution Order

1. **Smoke Tests (P0 Migration)**: `5.1-INT-003`
   - Must pass before any other tests
   - Validates database schema exists
   - **Time**: ~30 seconds

2. **P0 Critical Tests** (Blockers):
   - `5.1-INT-004` (FK constraint enforcement)
   - `5.1-INT-009` (FK validation)
   - `5.1-API-003` (Authorization - security)
   - `5.1-E2E-002` (Voice latency - performance)
   - **Time**: ~5 minutes
   - **Gate Impact**: FAIL if any P0 test fails

3. **P1 High-Priority Tests** (Core functionality):
   - All integration tests (DB operations, API endpoints)
   - E2E conversation flow tests
   - **Time**: ~10 minutes
   - **Gate Impact**: CONCERNS if P1 tests fail

4. **P2 Medium-Priority Tests** (Secondary features):
   - Metadata serialization
   - Pagination
   - Timestamp accuracy
   - **Time**: ~5 minutes
   - **Gate Impact**: PASS with notes

5. **P3 Low-Priority Tests** (Nice-to-have):
   - Migration rollback
   - **Time**: ~30 seconds
   - **Gate Impact**: None

### Execution Commands

```bash
# Smoke test only (migration)
pytest -m "p0 and integration" tests/integration/test_migration.py::test_5_1_INT_003

# P0 tests (critical blockers)
pytest -m p0

# P0 + P1 tests (core functionality)
pytest -m "p0 or p1"

# Full test suite (all priorities)
pytest tests/

# By test level
pytest -m unit         # Fast unit tests
pytest -m integration  # Integration tests (DB, API)
pytest -m e2e          # Full E2E tests (slowest)

# Performance tests only
pytest -m performance --benchmark-only
```

### CI/CD Integration

**GitHub Actions Workflow (.github/workflows/test-story-5-1.yml):**
```yaml
name: Test Story 5.1

on:
  pull_request:
    paths:
      - 'backend/app/models/conversation_message.py'
      - 'backend/alembic/versions/*conversation_message*'
      - 'backend/app/api/v1/endpoints/conversations.py'
      - 'backend/tests/integration/test_conversation_message.py'

jobs:
  test-p0:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:18-alpine
        env:
          POSTGRES_DB: numerologist_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5433:5432

    steps:
      - uses: actions/checkout@v3
      - name: Run P0 Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest -m p0 --verbose

      - name: Upload Coverage
        uses: codecov/codecov-action@v3

  test-p1:
    needs: test-p0
    runs-on: ubuntu-latest
    steps:
      - name: Run P1 Tests
        run: pytest -m p1 --verbose

  test-e2e:
    needs: test-p1
    runs-on: ubuntu-latest
    if: github.event.pull_request.base.ref == 'main'
    steps:
      - name: Run E2E Tests (Staging)
        env:
          DAILY_API_KEY: ${{ secrets.DAILY_API_KEY_STAGING }}
          DEEPGRAM_API_KEY: ${{ secrets.DEEPGRAM_API_KEY_STAGING }}
        run: pytest -m e2e --verbose
```

---

## Acceptance Criteria Traceability

| AC# | Acceptance Criterion | Test Scenarios | Status |
|-----|---------------------|----------------|--------|
| AC#1 | ConversationMessage model created | 5.1-UNIT-001, 5.1-INT-001 | ✅ Covered |
| AC#2 | Fields defined correctly | 5.1-UNIT-002, 5.1-INT-002 | ✅ Covered |
| AC#3 | Alembic migration with FK & indexes | 5.1-INT-003, 5.1-INT-004, 5.1-INT-005, 5.1-INT-006 | ✅ Covered |
| AC#4 | Messages saved asynchronously | 5.1-E2E-001, 5.1-INT-007, 5.1-INT-008 | ✅ Covered |
| AC#5 | Messages linked via FK | 5.1-INT-009, 5.1-INT-010 | ✅ Covered |
| AC#6 | Query messages (ordered, paginated) | 5.1-API-001, 5.1-API-002, 5.1-API-003 | ✅ Covered |
| AC#7 | Non-blocking operations (latency) | 5.1-E2E-002, 5.1-INT-011 | ✅ Covered |
| AC#8 | Both user & assistant messages captured | 5.1-E2E-003, 5.1-E2E-004, 5.1-INT-012 | ✅ Covered |

**Coverage**: 8/8 acceptance criteria have explicit test coverage (100%)

---

## Gate Decision Criteria

### Quality Gate Thresholds

**PASS Criteria:**
- All P0 tests pass (5 scenarios)
- All P1 tests pass (10 scenarios)
- Voice latency <3s validated (5.1-E2E-002)
- Authorization security validated (5.1-API-003)
- No high-priority risks (score ≥6) unmitigated

**CONCERNS Criteria:**
- P0 tests pass, but 1-2 P1 tests fail
- High-priority risks (R-001, R-002) have mitigation plans but not fully validated
- Voice latency 3-5s (degraded but functional)

**FAIL Criteria:**
- Any P0 test fails (migration, FK constraints, authorization, voice latency)
- High-priority security risk (R-002) not mitigated
- Voice latency >5s (unacceptable performance)

**WAIVED Criteria:**
- P0 test failures waived by Tech Lead + Product Manager
- Explicit risk acceptance documented with owner and expiry date

### Pre-Deployment Checklist

Before deploying Story 5.1 to production:

- [ ] All P0 tests pass (5/5)
- [ ] All P1 tests pass (10/10)
- [ ] Voice latency <3s validated in staging (5.1-E2E-002)
- [ ] Authorization check validated (5.1-API-003)
- [ ] Migration tested on staging database (5.1-INT-003)
- [ ] Error logging verified in staging logs (5.1-INT-008)
- [ ] Database indexes created and validated (5.1-INT-005)
- [ ] High-priority risks (R-001, R-002) mitigated and tested
- [ ] Code review completed (focus on async patterns, auth checks)
- [ ] Performance benchmarks meet targets (<50ms dispatch, <3s latency)

---

## Recommendations

### Immediate Actions (Before Development)

1. **Set up test database**: Docker container with PostgreSQL 18, run Alembic migrations
2. **Create test fixtures**: Implement fixtures in `conftest.py` for users, conversations, messages
3. **Configure CI/CD**: Add GitHub Actions workflow for automated P0/P1 test execution
4. **Review authorization pattern**: Ensure all conversation endpoints check `conversation.user_id == current_user.id`

### During Development

1. **Implement async patterns carefully**: Use `asyncio.create_task()` for fire-and-forget saves, not `await` in voice pipeline
2. **Add latency instrumentation**: Wrap message save operations with `LatencyTracker` for monitoring
3. **Test error handling early**: Simulate database failures (mock connection errors) to verify graceful degradation
4. **Validate indexes**: After migration, manually verify indexes exist with `\d+ conversation_message` in psql

### Testing Best Practices

1. **Run P0 tests first**: Migration must succeed before any other tests
2. **Use network-first interception in E2E**: Wait for API responses, not timeouts
3. **Parallelize integration tests**: Use pytest-xdist for faster execution
4. **Measure performance continuously**: Track async dispatch time in CI (fail if >50ms)
5. **Validate authorization in every test**: Never skip auth checks, even in test environments

### Post-Deployment Monitoring

1. **Track message save latency**: Alert if p95 >100ms (indicates DB contention)
2. **Monitor voice pipeline latency**: Alert if p95 >3s (NFR-P1 violation)
3. **Track save error rates**: Alert if error rate >1% (database issues)
4. **Review conversation query performance**: Monitor slow query logs for missing indexes

---

## Appendix

### Related Documents

- **Story**: `docs/stories/5-1-conversation-message-model-saving.md`
- **Story Context**: `docs/stories/5-1-conversation-message-model-saving.context.xml`
- **Architecture**: `docs/architecture.md` (Database Models, API Patterns)
- **PRD**: `docs/PRD.md` (NFR-P1: Voice Latency, NFR-S4: GDPR Compliance)
- **Epic**: `docs/epics.md` (Epic 5: Conversation Management)

### Knowledge Base References

- **Risk Governance**: `bmad/bmm/testarch/knowledge/risk-governance.md`
- **Probability-Impact Matrix**: `bmad/bmm/testarch/knowledge/probability-impact.md`
- **Test Levels Framework**: `bmad/bmm/testarch/knowledge/test-levels-framework.md`
- **Test Priorities Matrix**: `bmad/bmm/testarch/knowledge/test-priorities-matrix.md`

### Test File Structure

```
backend/tests/
├── conftest.py                          # Shared fixtures and test configuration
├── fixtures/
│   └── conversation_fixtures.py         # User, Conversation, Message fixtures
├── unit/
│   └── test_conversation_message_model.py   # 5.1-UNIT-001, 5.1-UNIT-002
├── integration/
│   ├── test_migration.py                # 5.1-INT-003, 5.1-INT-006
│   ├── test_conversation_message_db.py  # 5.1-INT-001, 5.1-INT-002, 5.1-INT-004, etc.
│   ├── test_message_api.py              # 5.1-API-001, 5.1-API-002, 5.1-API-003
│   └── test_message_performance.py      # 5.1-INT-007, 5.1-INT-011
└── e2e/
    └── test_conversation_flow.py        # 5.1-E2E-001, 5.1-E2E-002, 5.1-E2E-003, etc.
```

### Glossary

- **Async Save**: Non-blocking database write operation using asyncio.create_task() or background tasks
- **FK Constraint**: Foreign Key database constraint ensuring referential integrity (conversation_id must exist)
- **P0-P3 Priority**: Test priority levels (P0=Critical, P1=High, P2=Medium, P3=Low)
- **Risk Score**: Probability × Impact (1-9 scale), determines action threshold
- **Voice Latency**: Time from user speech end to AI audio start (target <3s per NFR-P1)
- **Authorization**: Verification that authenticated user owns the resource they're accessing (not just authentication)
- **Graceful Degradation**: System continues functioning when subsystem (e.g., database) fails

---

**Document Status**: ✅ Complete
**Review Required**: Yes (Tech Lead, QA Lead)
**Next Steps**: Implement tests, validate migration, execute P0 tests

---

*Generated by BMAD Master Test Architect (Murat) using BMM Test Design Workflow v1.0*
*Risk-based testing methodology with probability-impact scoring (1-9 scale)*
*Test coverage: 22 scenarios across 4 levels (Unit, Integration, API, E2E)*
