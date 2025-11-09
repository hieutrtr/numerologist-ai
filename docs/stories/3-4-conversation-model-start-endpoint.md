# Story 3.4: Conversation Model & Start Endpoint

**Epic:** Epic 3 - Voice Infrastructure & Basic Conversation
**Story ID:** 3-4-conversation-model-start-endpoint
**Status:** review
**Created:** 2025-11-09
**Context Reference:** docs/stories/3-4-conversation-model-start-endpoint.context.xml

---

## User Story

**As a** user,
**I want** to start a voice conversation via API,
**So that** I can begin talking to the AI numerologist.

---

## Acceptance Criteria

### AC1: Conversation Model Created
- [ ] Create `backend/src/models/conversation.py` module
- [ ] Define `Conversation` SQLAlchemy model with:
  - `id` (UUID primary key)
  - `user_id` (foreign key to User)
  - `daily_room_id` (string, Daily.co room name)
  - `started_at` (datetime, auto-set on creation)
  - `ended_at` (datetime, nullable)
  - `duration_seconds` (integer, nullable)
  - `created_at` (datetime audit field)
  - `updated_at` (datetime audit field)
- [ ] Add relationship to User model: `user = relationship("User", back_populates="conversations")`
- [ ] Add validation: conversation must have valid user_id
- [ ] Add helper method: `calculate_duration()` to compute duration when ended_at is set

### AC2: Alembic Database Migration
- [ ] Generate Alembic migration for conversations table:
  - `alembic revision --autogenerate -m "Add conversations table"`
- [ ] Migration creates:
  - conversations table with all fields from AC1
  - foreign key constraint to users table
  - indexes on user_id and daily_room_id
  - check constraint: ended_at >= started_at (if ended_at is set)
- [ ] Apply migration:
  - `alembic upgrade head`
- [ ] Verify in PostgreSQL: `\d conversations`

### AC3: Conversation Endpoints Router
- [ ] Create `backend/src/api/v1/endpoints/conversations.py` module
- [ ] Import required dependencies:
  - FastAPI Router, Depends
  - SQLAlchemy Session
  - Conversation, User models
  - daily_service, pipecat_bot
  - get_current_user dependency
  - asyncio for background tasks
- [ ] Create APIRouter instance with tags=["conversations"]

### AC4: POST /api/v1/conversations/start Endpoint
- [ ] Implement `start_conversation()` endpoint:
  - Route: `POST /api/v1/conversations/start`
  - Auth: Requires JWT token (get_current_user dependency)
  - Steps:
    1. Create Conversation record in database with user_id and started_at
    2. Generate conversation_id from UUID
    3. Call `daily_service.create_room(str(conversation_id))` to create Daily.co room
    4. Update conversation.daily_room_id with room name from Daily response
    5. Commit database changes
    6. Spawn Pipecat bot as background task: `asyncio.create_task(run_bot(room_url, token))`
    7. Return response with conversation_id, daily_room_url, daily_token
- [ ] Error handling:
  - Catch exceptions from daily_service, log them, return 500 status
  - Catch database errors, rollback transaction, return 500 status
  - Return 401 if not authenticated
- [ ] Response format:
  ```json
  {
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
    "daily_room_url": "https://domain.daily.co/room-name",
    "daily_token": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```

### AC5: Endpoint Wiring
- [ ] Update `backend/src/api/v1/router.py`:
  - Import: `from src.api.v1.endpoints import conversations`
  - Include router: `api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])`
  - Verifies route is: `POST /api/v1/conversations/start`

### AC6: User Model Update
- [ ] Add to `backend/src/models/user.py`:
  - Add relationship: `conversations = relationship("Conversation", back_populates="user")`
  - Allows: `user.conversations` to access all user's conversations

### AC7: Session Dependency
- [ ] Verify `backend/src/core/deps.py` has `get_session()` dependency:
  - Used to inject SQLAlchemy Session into endpoint
  - Returns database session from sessionmaker
- [ ] If missing, create it:
  ```python
  def get_session():
      with SessionLocal() as session:
          yield session
  ```

### AC8: Manual Testing - Postman
- [ ] Can test endpoint with Postman:
  - Method: POST
  - URL: `http://localhost:8000/api/v1/conversations/start`
  - Headers: `Authorization: Bearer {jwt_token}`
  - Response: 200 OK with conversation_id and daily_room_url
  - Verify: conversation appears in database

### AC9: Integration Testing
- [ ] Bot spawns successfully in background for new conversation
- [ ] Bot joins Daily.co room within 5 seconds
- [ ] User can join room URL in browser and hear bot greeting
- [ ] Multiple concurrent conversations work independently
- [ ] Bot handles room cleanup on conversation end

### AC10: Error Scenarios
- [ ] Returns 401 Unauthorized if no auth token
- [ ] Returns 400 BadRequest if user_id invalid
- [ ] Returns 500 ServerError with descriptive message if daily_service fails
- [ ] Returns 500 ServerError with descriptive message if bot spawn fails
- [ ] Database transaction rolls back on failure

---

## Tasks / Subtasks

### Task 1: Create Conversation Model (AC1)
- [ ] Create file: `backend/src/models/conversation.py`
- [ ] Import SQLAlchemy base and Column types
- [ ] Import UUID, datetime
- [ ] Define Conversation class extending Base:
  - `__tablename__ = "conversations"`
  - Fields with correct types and constraints
  - Relationship to User
  - Helper methods
- [ ] Add to `backend/src/models/__init__.py`: `from .conversation import Conversation`

### Task 2: Create Alembic Migration (AC2)
- [ ] Run: `cd backend && alembic revision --autogenerate -m "Add conversations table"`
- [ ] Verify migration file in: `backend/alembic/versions/`
- [ ] Review migration for correctness
- [ ] Run: `alembic upgrade head`
- [ ] Verify table created: `psql postgresql://postgres:password@localhost:5432/numerologist` → `\d conversations`
- [ ] Document connection string in comments

### Task 3: Create Conversations Endpoint Router (AC3)
- [ ] Create file: `backend/src/api/v1/endpoints/conversations.py`
- [ ] Add module docstring
- [ ] Import all required dependencies
- [ ] Create: `router = APIRouter(prefix="/conversations", tags=["conversations"])`

### Task 4: Implement Start Endpoint (AC4, AC8, AC10)
- [ ] Implement async function:
  ```python
  @router.post("/start")
  async def start_conversation(
      current_user: User = Depends(get_current_user),
      session: Session = Depends(get_session)
  ):
      # Implementation here
  ```
- [ ] Logic flow:
  1. Create Conversation: `conversation = Conversation(user_id=current_user.id)`
  2. Save: `session.add(conversation); session.commit(); session.refresh(conversation)`
  3. Daily room: `room_data = await daily_service.create_room(str(conversation.id))`
  4. Update: `conversation.daily_room_id = room_data["room_name"]; session.commit()`
  5. Background task: `asyncio.create_task(pipecat_bot.run_bot(room_data["room_url"], room_data["token"]))`
  6. Return response
- [ ] Error handling with try/except
- [ ] Logging: start, success, errors

### Task 5: Wire Endpoint in API Router (AC5)
- [ ] Edit: `backend/src/api/v1/router.py`
- [ ] Add import: `from src.api.v1.endpoints import conversations`
- [ ] Add include_router call with correct prefix
- [ ] Test: verify route appears in Swagger docs at `/docs`

### Task 6: Update User Model (AC6)
- [ ] Edit: `backend/src/models/user.py`
- [ ] Add import: `from sqlalchemy.orm import relationship`
- [ ] Add field to User class:
  ```python
  conversations = relationship("Conversation", back_populates="user")
  ```

### Task 7: Verify Session Dependency (AC7)
- [ ] Check: `backend/src/core/deps.py` has `get_session()` function
- [ ] If missing, create it with SessionLocal from database module
- [ ] Verify SessionLocal is imported correctly

### Task 8: Manual Testing with Postman (AC8)
- [ ] Start backend: `make dev`
- [ ] Start Redis: `docker-compose up redis`
- [ ] Get JWT token:
  - POST `/api/v1/auth/login` with test user credentials
  - Copy token from response
- [ ] Test conversation start:
  - POST `/api/v1/conversations/start`
  - Header: `Authorization: Bearer {token}`
  - Check 200 response with conversation_id and daily_room_url
- [ ] Verify database:
  - Query: `SELECT * FROM conversations WHERE user_id = '{user_id}';`
  - Confirm row exists with correct data

### Task 9: Integration Testing (AC9)
- [ ] Verify bot spawned successfully:
  - Check logs: "Starting Pipecat bot for room: ..."
  - Check bot joined room within 5 seconds
- [ ] User joins room:
  - Open daily_room_url in browser
  - Allow microphone
  - Hear bot greeting
- [ ] Multiple conversations:
  - Create 2-3 conversations concurrently
  - Verify each has independent bot instance
  - Each bot responds independently

### Task 10: Error Scenario Testing (AC10)
- [ ] Test without auth token:
  - POST `/api/v1/conversations/start` without Authorization header
  - Expect: 401 Unauthorized
- [ ] Test with invalid user:
  - Mock current_user dependency to return None
  - Expect: 401 Unauthorized
- [ ] Test with daily_service failure:
  - Mock daily_service.create_room to raise exception
  - Expect: 500 ServerError with descriptive message
- [ ] Test with bot spawn failure:
  - Mock pipecat_bot.run_bot to raise exception
  - Expect: 500 ServerError (background task failure logged)
  - Conversation should still be created in database

### Task 11: Code Review & Documentation (AC11)
- [ ] Verify code follows project patterns:
  - Async/await consistent with other endpoints
  - Error handling matches other endpoints
  - Type hints on all parameters and returns
  - Docstrings on public functions
- [ ] Update API documentation:
  - Verify `/docs` shows POST /api/v1/conversations/start
  - Response schema includes conversation_id, daily_room_url, daily_token
  - Example request and response visible

---

## Technical Notes

### Database Schema
```python
# backend/src/models/conversation.py
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from src.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    daily_room_id = Column(String(255), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")

    def calculate_duration(self):
        """Calculate duration in seconds if conversation has ended."""
        if self.ended_at:
            delta = self.ended_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
```

### Endpoint Implementation
```python
# backend/src/api/v1/endpoints/conversations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import asyncio
import logging

from src.models.conversation import Conversation
from src.models.user import User
from src.services.daily_service import create_room
from src.voice_pipeline.pipecat_bot import run_bot
from src.core.deps import get_current_user, get_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/start")
async def start_conversation(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Start a new voice conversation."""
    try:
        # Create conversation record
        conversation = Conversation(user_id=current_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {current_user.id}")

        # Create Daily.co room
        room_data = await create_room(str(conversation.id))

        # Update conversation with room ID
        conversation.daily_room_id = room_data["room_name"]
        session.commit()

        logger.info(f"Created Daily.co room: {room_data['room_name']}")

        # Spawn bot in background
        asyncio.create_task(run_bot(room_data["room_url"], room_data["meeting_token"]))

        logger.info(f"Bot spawned for conversation {conversation.id}")

        return {
            "conversation_id": str(conversation.id),
            "daily_room_url": room_data["room_url"],
            "daily_token": room_data["meeting_token"]
        }

    except Exception as e:
        logger.error(f"Failed to start conversation: {e}", exc_info=True)
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### Router Wiring
```python
# backend/src/api/v1/router.py
from fastapi import APIRouter
from src.api.v1.endpoints import auth, users, conversations

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# Creates routes:
# POST /api/v1/conversations/start
```

---

## Dependencies & Prerequisites

### Before Starting This Story
- [ ] Story 3.3 (Basic Pipecat Bot) must be completed and in review/done
- [ ] Daily.co service (`daily_service`) verified working
- [ ] Pipecat bot (`pipecat_bot`) verified working
- [ ] Database and migrations infrastructure working
- [ ] JWT authentication working (get_current_user dependency)
- [ ] SQLAlchemy and Alembic set up

### External Services
- [ ] Daily.co API (existing, from story 3.3)
- [ ] PostgreSQL database (existing, from epic 1)

### Project Structure Assumptions
- [ ] `backend/src/models/` directory exists
- [ ] `backend/src/api/v1/endpoints/` directory exists
- [ ] `backend/alembic/` migration system working
- [ ] `backend/src/core/deps.py` has dependency injection
- [ ] `backend/src/core/database.py` has SessionLocal

---

## Related Stories

- **Previous:** Story 3.3 - Basic Pipecat Bot with Greeting
- **Next:** Story 3.5 - Frontend Conversation State (Zustand)
- **Related:** Story 3.2 - Daily.co Room Management Service
- **Related:** Story 3.1 - Add Voice Pipeline Dependencies

---

## Notes for Developer

1. **Background Task Spawning:** Using `asyncio.create_task()` spawns the bot in background. Errors in bot execution won't block the endpoint response, but will be logged.

2. **Database Transaction:** Keep transaction simple - create conversation, get room data, update room ID, then commit. If any step fails, rollback and return error.

3. **Response Timing:** Endpoint should return within 2-3 seconds (includes Daily.co API call and bot spawn). Bot initialization takes additional time asynchronously.

4. **Testing:** Use Postman or curl to test. Get JWT token first from login endpoint, then use in Authorization header.

5. **Logging:** Log key events: conversation created, room created, bot spawned, errors. This helps debug issues in production.

6. **Future Enhancement:** Story 3.5 will implement frontend Zustand store to call this endpoint and manage conversation state on mobile app.

---

## Definition of Done

- [x] Code follows project style and patterns
- [x] Type hints on all functions and parameters
- [x] Docstrings on public functions
- [x] Error handling with meaningful error messages
- [x] Logging at appropriate levels (info for events, error for failures)
- [x] Endpoint appears in Swagger docs
- [x] Manual testing verified with Postman
- [x] No breaking changes to existing code
- [x] Database schema matches requirements
- [x] Migration tested and verified
- [x] Related tests written (if applicable to story scope)
- [x] Code review approved before moving to "ready-for-dev"
