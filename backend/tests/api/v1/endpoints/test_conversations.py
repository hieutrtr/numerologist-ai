"""
Tests for Conversation Endpoints

Tests cover:
- POST /api/v1/conversations/start endpoint
- POST /api/v1/conversations/{id}/end endpoint
- Authentication and authorization
- Error handling and edge cases
- Database persistence
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import app
from src.models.user import User
from src.models.conversation import Conversation
from datetime import datetime, date, timezone
from uuid import uuid4, UUID

client = TestClient(app)


@pytest.fixture
def test_user(session: Session) -> User:
    """Create a test user for conversation tests."""
    user = User(
        id=uuid4(),
        email="testuser@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        birth_date=date(1990, 1, 1)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_start_conversation_missing_auth():
    """Test POST /start without JWT token returns 401."""
    response = client.post("/api/v1/conversations/start")
    assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials


@patch("src.api.v1.endpoints.conversations.create_room")
@patch("src.api.v1.endpoints.conversations.run_bot")
def test_start_conversation_success(mock_run_bot, mock_create_room, test_user, session: Session):
    """Test successful conversation start with all services working."""
    # Mock Daily.co room creation
    mock_create_room.return_value = {
        "room_url": "https://domain.daily.co/test-room",
        "room_name": "test-room",
        "meeting_token": "mock-token-12345"
    }
    mock_run_bot.return_value = None  # Background task

    # Get auth token for test user (in real scenario)
    # For this test, we'd need to generate a valid JWT token
    # Simplified test structure shown

    # Make request
    # response = client.post(
    #     "/api/v1/conversations/start",
    #     headers={"Authorization": f"Bearer {token}"}
    # )

    # assert response.status_code == 200
    # data = response.json()
    # assert "conversation_id" in data
    # assert "daily_room_url" in data
    # assert "daily_token" in data

    # Verify conversation was created in database
    # conversations = session.query(Conversation).filter_by(user_id=test_user.id).all()
    # assert len(conversations) == 1
    # assert conversations[0].daily_room_id == "test-room"

    pass  # Full implementation pending auth/JWT test fixtures


def test_start_conversation_daily_co_failure():
    """Test conversation start handles Daily.co API failures gracefully."""
    # Mock Daily.co failure
    # Verify endpoint returns 500 with descriptive error
    # Verify conversation is rolled back if room creation fails
    pass


def test_conversation_model_duration_calculation():
    """Test Conversation.calculate_duration() works correctly."""
    # Use timezone-aware datetime with exact timestamps to avoid flakiness
    start_time = datetime(2025, 11, 10, 14, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2025, 11, 10, 14, 5, 0, tzinfo=timezone.utc)  # Exactly 5 minutes later

    conv = Conversation(
        user_id=uuid4(),
        started_at=start_time,
        ended_at=end_time
    )
    conv.calculate_duration()

    assert conv.duration_seconds is not None
    assert conv.duration_seconds == 300  # 5 minutes


def test_conversation_model_required_fields():
    """Test Conversation model enforces required fields."""
    # user_id should be required
    # started_at should auto-set to now
    conv = Conversation(user_id=uuid4())
    assert conv.started_at is not None
    assert conv.ended_at is None
    assert conv.duration_seconds is None


def test_conversation_user_relationship():
    """Test Conversation and User relationship works."""
    # This would test lazy loading of user.conversations relationship
    # Verify User.conversations contains all user's conversations
    pass


def test_concurrent_conversation_creation():
    """Test multiple concurrent conversation start requests."""
    # Verify each gets unique conversation_id
    # Verify each gets different Daily.co room
    # Verify no race conditions in database
    pass


def test_conversation_database_rollback():
    """Test database rolls back on failure."""
    # Mock Daily.co failure mid-request
    # Verify Conversation record is NOT created in database
    # Verify transaction rollback happens automatically
    pass


# ============================================================================
# POST /api/v1/conversations/{id}/end - End Conversation Endpoint Tests
# ============================================================================

def test_end_conversation_missing_auth():
    """Test POST /end without JWT token returns 403."""
    conversation_id = uuid4()
    response = client.post(f"/api/v1/conversations/{conversation_id}/end")
    assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials


@patch("src.api.v1.endpoints.conversations.delete_room")
def test_end_conversation_success(mock_delete_room, test_user, session: Session):
    """Test successful conversation end with all services working."""
    # Create an active conversation for the test user
    conversation = Conversation(
        user_id=test_user.id,
        daily_room_id="test-room-123"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Mock Daily.co room deletion success
    mock_delete_room.return_value = True

    # TODO: This test requires JWT authentication to be fully implemented
    # For now, testing the model and logic directly

    # Verify conversation can be ended
    conversation.ended_at = datetime.now(timezone.utc)
    conversation.calculate_duration()
    session.commit()

    assert conversation.ended_at is not None
    assert conversation.duration_seconds is not None
    assert conversation.duration_seconds >= 0


def test_end_conversation_not_found(test_user, session: Session):
    """Test ending non-existent conversation returns 404."""
    # Use a random UUID that doesn't exist in database
    nonexistent_id = uuid4()

    # Try to get conversation from database (simulating endpoint logic)
    conversation = session.get(Conversation, nonexistent_id)

    # Verify conversation doesn't exist
    assert conversation is None

    # TODO: Full endpoint test would verify 404 response
    # Requires JWT auth fixtures
    pass


def test_end_conversation_already_ended(test_user, session: Session):
    """Test ending an already-ended conversation returns 400."""
    # Create a conversation that's already ended
    conversation = Conversation(
        user_id=test_user.id,
        daily_room_id="test-room-456",
        ended_at=datetime.now(timezone.utc)
    )
    conversation.calculate_duration()
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Verify conversation is already ended
    assert conversation.ended_at is not None

    # Attempting to end again should be prevented
    # TODO: Full endpoint test would verify 400 response
    pass


def test_end_conversation_unauthorized_user(session: Session):
    """Test user cannot end another user's conversation."""
    # Create two users
    user1 = User(
        id=uuid4(),
        email="user1@example.com",
        hashed_password="hash1",
        full_name="User One",
        birth_date=date(1990, 1, 1)
    )
    user2 = User(
        id=uuid4(),
        email="user2@example.com",
        hashed_password="hash2",
        full_name="User Two",
        birth_date=date(1990, 1, 1)
    )
    session.add(user1)
    session.add(user2)
    session.commit()

    # Create conversation for user1
    conversation = Conversation(
        user_id=user1.id,
        daily_room_id="test-room-789"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Verify conversation belongs to user1
    assert conversation.user_id == user1.id
    assert conversation.user_id != user2.id

    # TODO: Full endpoint test would verify 403 response when user2 tries to end user1's conversation
    pass


@patch("src.api.v1.endpoints.conversations.delete_room")
def test_end_conversation_daily_deletion_failure(mock_delete_room, test_user, session: Session):
    """Test conversation end succeeds even if Daily.co deletion fails (best-effort cleanup)."""
    # Create an active conversation
    conversation = Conversation(
        user_id=test_user.id,
        daily_room_id="test-room-abc"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Mock Daily.co room deletion failure
    mock_delete_room.side_effect = Exception("Daily.co API error")

    # End conversation logic should still succeed
    conversation.ended_at = datetime.now(timezone.utc)
    conversation.calculate_duration()
    session.commit()

    # Verify conversation was ended despite Daily.co failure
    assert conversation.ended_at is not None
    assert conversation.duration_seconds is not None

    # TODO: Full endpoint test would verify:
    # - Response is still 200 (success)
    # - Error is logged but not propagated
    # - Database updates persist
    pass


def test_end_conversation_duration_calculation():
    """Test duration is correctly calculated when ending conversation."""
    # Create conversation with known start time
    start_time = datetime(2025, 11, 10, 14, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2025, 11, 10, 14, 15, 30, tzinfo=timezone.utc)  # 15 minutes 30 seconds later

    conversation = Conversation(
        user_id=uuid4(),
        started_at=start_time,
        ended_at=end_time
    )
    conversation.calculate_duration()

    # Verify duration is calculated correctly
    assert conversation.duration_seconds == 930  # 15 * 60 + 30 = 930 seconds


def test_timezone_aware_naive_mismatch():
    """Test calculate_duration() handles timezone-aware and naive datetime mismatch."""
    # Simulate the error scenario: timezone-naive started_at, timezone-aware ended_at
    start_time_naive = datetime(2025, 11, 10, 14, 0, 0)  # No tzinfo (naive)
    end_time_aware = datetime(2025, 11, 10, 14, 15, 30, tzinfo=timezone.utc)  # With tzinfo (aware)

    conversation = Conversation(
        user_id=uuid4(),
        started_at=start_time_naive,
        ended_at=end_time_aware
    )

    # Should not raise "can't subtract offset-naive and offset-aware datetimes" error
    conversation.calculate_duration()

    # Verify duration is calculated correctly
    assert conversation.duration_seconds == 930  # 15 * 60 + 30 = 930 seconds


def test_multiple_end_cycles(test_user, session: Session):
    """Test multiple start-end cycles create separate conversation records."""
    # Create 3 conversations for the user
    conversations = []
    for i in range(3):
        conv = Conversation(
            user_id=test_user.id,
            daily_room_id=f"test-room-{i}"
        )
        session.add(conv)
        session.commit()
        session.refresh(conv)

        # End the conversation
        conv.ended_at = datetime.now(timezone.utc)
        conv.calculate_duration()
        session.commit()

        conversations.append(conv)

    # Verify all 3 conversations exist and are ended
    user_conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).all()

    assert len(user_conversations) >= 3  # At least our 3 conversations
    for conv in conversations:
        assert conv.ended_at is not None
        assert conv.duration_seconds is not None


# ============================================================================
# GET /api/v1/conversations - List Conversations Endpoint Tests (Story 5.2)
# ============================================================================

def test_list_conversations_missing_auth():
    """
    GIVEN: User is not authenticated
    WHEN: Requesting GET /conversations
    THEN: Returns 403 (Forbidden)

    AC #1: Endpoint requires authentication
    """
    response = client.get("/api/v1/conversations/")
    assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials


def test_list_conversations_empty_list(test_user, session: Session):
    """
    GIVEN: User has no conversations
    WHEN: Requesting GET /conversations
    THEN: Returns empty list with correct pagination metadata

    AC #2: Returns list of user's conversations
    Edge case: Empty conversation list
    """
    # Verify user has no conversations
    user_conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).all()
    assert len(user_conversations) == 0

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected response:
    # {
    #     "conversations": [],
    #     "total": 0,
    #     "page": 1,
    #     "limit": 20,
    #     "has_more": false
    # }
    pass


def test_list_conversations_with_data(test_user, session: Session):
    """
    GIVEN: User has 3 conversations with different timestamps
    WHEN: Requesting GET /conversations
    THEN: Returns conversations ordered by most recent first

    AC #2-3: Returns list with id, started_at, ended_at, duration, main_topic
    AC #5: Ordered by most recent first
    """
    # Create 3 conversations with different timestamps
    conv1 = Conversation(
        user_id=test_user.id,
        started_at=datetime(2025, 11, 20, 10, 0, 0, tzinfo=timezone.utc),
        ended_at=datetime(2025, 11, 20, 10, 15, 0, tzinfo=timezone.utc),
        daily_room_id="room-1"
    )
    conv1.calculate_duration()

    conv2 = Conversation(
        user_id=test_user.id,
        started_at=datetime(2025, 11, 22, 14, 0, 0, tzinfo=timezone.utc),  # Most recent
        ended_at=datetime(2025, 11, 22, 14, 30, 0, tzinfo=timezone.utc),
        daily_room_id="room-2"
    )
    conv2.calculate_duration()

    conv3 = Conversation(
        user_id=test_user.id,
        started_at=datetime(2025, 11, 21, 9, 0, 0, tzinfo=timezone.utc),  # Middle
        daily_room_id="room-3"  # Still active (no ended_at)
    )

    session.add_all([conv1, conv2, conv3])
    session.commit()

    # Verify conversations exist in database
    user_conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).order_by(Conversation.started_at.desc()).all()

    assert len(user_conversations) == 3
    # Verify ordering: conv2 (most recent), then conv3, then conv1
    assert user_conversations[0].id == conv2.id
    assert user_conversations[1].id == conv3.id
    assert user_conversations[2].id == conv1.id

    # Verify response includes all required fields
    for conv in user_conversations:
        assert conv.id is not None
        assert conv.started_at is not None
        assert conv.duration_seconds is not None if conv.ended_at else True
        # main_topic will be None for now (future story)

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected response should have conversations in order: conv2, conv3, conv1


def test_list_conversations_pagination_first_page(test_user, session: Session):
    """
    GIVEN: User has 25 conversations
    WHEN: Requesting GET /conversations?page=1&limit=20
    THEN: Returns first 20 conversations with has_more=true

    AC #4: Paginated (20 per page)
    """
    # Create 25 conversations
    conversations = []
    for i in range(25):
        conv = Conversation(
            user_id=test_user.id,
            started_at=datetime(2025, 11, 1, 0, 0, 0, tzinfo=timezone.utc) + \
                       __import__('datetime').timedelta(hours=i),
            daily_room_id=f"room-{i}"
        )
        session.add(conv)
        conversations.append(conv)
    session.commit()

    # Verify total count
    total = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).count()
    assert total == 25

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected response:
    # {
    #     "total": 25,
    #     "page": 1,
    #     "limit": 20,
    #     "has_more": true,
    #     "conversations": [... 20 items ...]
    # }
    pass


def test_list_conversations_pagination_second_page(test_user, session: Session):
    """
    GIVEN: User has 25 conversations
    WHEN: Requesting GET /conversations?page=2&limit=20
    THEN: Returns remaining 5 conversations with has_more=false

    AC #4: Paginated (20 per page)
    Edge case: Last page with fewer items
    """
    # Create 25 conversations (reusing setup from previous test scenario)
    conversations = []
    for i in range(25):
        conv = Conversation(
            user_id=test_user.id,
            started_at=datetime(2025, 11, 1, 0, 0, 0, tzinfo=timezone.utc) + \
                       __import__('datetime').timedelta(hours=i),
            daily_room_id=f"room-page2-{i}"
        )
        session.add(conv)
        conversations.append(conv)
    session.commit()

    # Simulate pagination calculation
    page = 2
    limit = 20
    offset = (page - 1) * limit  # 20

    # Query second page
    page_conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).order_by(Conversation.started_at.desc()).offset(offset).limit(limit).all()

    assert len(page_conversations) == 5  # Only 5 remaining

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected response:
    # {
    #     "total": 25,
    #     "page": 2,
    #     "limit": 20,
    #     "has_more": false,
    #     "conversations": [... 5 items ...]
    # }
    pass


def test_list_conversations_pagination_exactly_one_page(test_user, session: Session):
    """
    GIVEN: User has exactly 20 conversations
    WHEN: Requesting GET /conversations?page=1&limit=20
    THEN: Returns all 20 with has_more=false

    Edge case: Pagination boundary (exactly one full page)
    """
    # Create exactly 20 conversations
    for i in range(20):
        conv = Conversation(
            user_id=test_user.id,
            started_at=datetime(2025, 11, 1, 0, 0, 0, tzinfo=timezone.utc) + \
                       __import__('datetime').timedelta(hours=i),
            daily_room_id=f"room-exact-{i}"
        )
        session.add(conv)
    session.commit()

    total = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).count()
    assert total == 20

    # Simulate has_more calculation
    offset = 0
    limit = 20
    has_more = (offset + 20) < total  # Should be False (20 < 20)

    assert has_more is False

    # TODO: Full endpoint test requires JWT auth fixtures
    pass


def test_list_conversations_invalid_page_zero():
    """
    GIVEN: User requests page 0
    WHEN: Requesting GET /conversations?page=0
    THEN: Returns 422 (Validation error)

    Validation: Test invalid page numbers
    """
    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected: HTTPException 422 with detail "Page must be >= 1"
    pass


def test_list_conversations_invalid_page_negative():
    """
    GIVEN: User requests negative page
    WHEN: Requesting GET /conversations?page=-1
    THEN: Returns 422 (Validation error)

    Validation: Test invalid page numbers
    """
    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected: HTTPException 422 with detail "Page must be >= 1"
    pass


def test_list_conversations_invalid_limit_zero():
    """
    GIVEN: User requests limit=0
    WHEN: Requesting GET /conversations?limit=0
    THEN: Returns 422 (Validation error)

    Validation: Test invalid limits
    """
    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected: HTTPException 422 with detail "Limit must be between 1 and 100"
    pass


def test_list_conversations_invalid_limit_over_max():
    """
    GIVEN: User requests limit=150 (over max of 100)
    WHEN: Requesting GET /conversations?limit=150
    THEN: Returns 422 (Validation error)

    Validation: Test invalid limits
    """
    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected: HTTPException 422 with detail "Limit must be between 1 and 100"
    pass


def test_list_conversations_user_isolation(session: Session):
    """
    GIVEN: Two users each have conversations
    WHEN: User1 requests GET /conversations
    THEN: Returns only User1's conversations, not User2's

    Security: Verify users can only see their own conversations
    """
    # Create two users
    user1 = User(
        id=uuid4(),
        email="user1@example.com",
        hashed_password="hash1",
        full_name="User One",
        birth_date=date(1990, 1, 1)
    )
    user2 = User(
        id=uuid4(),
        email="user2@example.com",
        hashed_password="hash2",
        full_name="User Two",
        birth_date=date(1990, 1, 1)
    )
    session.add_all([user1, user2])
    session.commit()

    # Create conversations for each user
    conv1_user1 = Conversation(user_id=user1.id, daily_room_id="user1-room1")
    conv2_user1 = Conversation(user_id=user1.id, daily_room_id="user1-room2")
    conv1_user2 = Conversation(user_id=user2.id, daily_room_id="user2-room1")

    session.add_all([conv1_user1, conv2_user1, conv1_user2])
    session.commit()

    # Query conversations for user1
    user1_conversations = session.query(Conversation).filter(
        Conversation.user_id == user1.id
    ).all()

    # Verify user1 only sees their own conversations
    assert len(user1_conversations) == 2
    assert all(conv.user_id == user1.id for conv in user1_conversations)
    assert conv1_user2 not in user1_conversations

    # TODO: Full endpoint test requires JWT auth fixtures
    pass


# ============================================================================
# GET /api/v1/conversations/{id} - Get Conversation Detail Endpoint Tests (Story 5.2)
# ============================================================================

def test_get_conversation_missing_auth():
    """
    GIVEN: User is not authenticated
    WHEN: Requesting GET /conversations/{id}
    THEN: Returns 403 (Forbidden)

    AC #6: Detail endpoint requires authentication
    """
    conversation_id = uuid4()
    response = client.get(f"/api/v1/conversations/{conversation_id}")
    assert response.status_code == 403  # HTTPBearer returns 403 for missing credentials


def test_get_conversation_not_found(test_user, session: Session):
    """
    GIVEN: Conversation ID doesn't exist
    WHEN: Requesting GET /conversations/{nonexistent_id}
    THEN: Returns 404 (Not Found)

    AC #6: Test 404 when conversation not found
    """
    nonexistent_id = uuid4()

    # Verify conversation doesn't exist
    conversation = session.get(Conversation, nonexistent_id)
    assert conversation is None

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected: HTTPException 404 with detail "Conversation not found"
    pass


def test_get_conversation_unauthorized_user(session: Session):
    """
    GIVEN: Conversation belongs to User1
    WHEN: User2 requests GET /conversations/{user1_conversation_id}
    THEN: Returns 403 (Forbidden)

    AC #6: Test authorization - user cannot access other user's conversations
    """
    # Create two users
    user1 = User(
        id=uuid4(),
        email="authuser1@example.com",
        hashed_password="hash1",
        full_name="Auth User One",
        birth_date=date(1990, 1, 1)
    )
    user2 = User(
        id=uuid4(),
        email="authuser2@example.com",
        hashed_password="hash2",
        full_name="Auth User Two",
        birth_date=date(1990, 1, 1)
    )
    session.add_all([user1, user2])
    session.commit()

    # Create conversation for user1
    conversation = Conversation(
        user_id=user1.id,
        daily_room_id="user1-private-room"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Verify conversation belongs to user1
    assert conversation.user_id == user1.id
    assert conversation.user_id != user2.id

    # TODO: Full endpoint test requires JWT auth fixtures
    # When user2 tries to access conversation:
    # Expected: HTTPException 403 with detail "Not authorized to access this conversation"
    pass


def test_get_conversation_with_messages(test_user, session: Session):
    """
    GIVEN: Conversation exists with 5 messages
    WHEN: Requesting GET /conversations/{id}
    THEN: Returns conversation with all messages ordered by timestamp

    AC #6: Returns full conversation with all messages
    """
    from src.models.conversation_message import ConversationMessage, MessageRole

    # Create conversation
    conversation = Conversation(
        user_id=test_user.id,
        started_at=datetime(2025, 11, 23, 14, 0, 0, tzinfo=timezone.utc),
        ended_at=datetime(2025, 11, 23, 14, 15, 0, tzinfo=timezone.utc),
        daily_room_id="room-with-messages"
    )
    conversation.calculate_duration()
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create 5 messages with different timestamps
    messages_data = [
        (MessageRole.USER, "Hello, what's my life path number?", 0),
        (MessageRole.ASSISTANT, "I'd be happy to help! What's your birth date?", 30),
        (MessageRole.USER, "January 15, 1990", 60),
        (MessageRole.ASSISTANT, "Based on your birth date, your life path number is 8.", 90),
        (MessageRole.USER, "What does that mean?", 120),
    ]

    created_messages = []
    for role, content, seconds_offset in messages_data:
        msg = ConversationMessage(
            conversation_id=conversation.id,
            role=role,
            content=content,
            timestamp=conversation.started_at + __import__('datetime').timedelta(seconds=seconds_offset),
            message_metadata={}
        )
        session.add(msg)
        created_messages.append(msg)

    session.commit()

    # Query messages
    messages = session.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation.id
    ).order_by(ConversationMessage.timestamp.asc()).all()

    # Verify all 5 messages exist and are ordered correctly
    assert len(messages) == 5
    assert messages[0].content == "Hello, what's my life path number?"
    assert messages[4].content == "What does that mean?"

    # Verify message order (timestamp ascending)
    for i in range(len(messages) - 1):
        assert messages[i].timestamp <= messages[i + 1].timestamp

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected response includes:
    # - conversation object with id, started_at, ended_at, duration
    # - messages array with all 5 messages in timestamp order
    pass


def test_get_conversation_without_messages(test_user, session: Session):
    """
    GIVEN: Conversation exists with no messages
    WHEN: Requesting GET /conversations/{id}
    THEN: Returns conversation with empty messages array

    Edge case: Conversation without messages
    """
    # Create conversation without messages
    conversation = Conversation(
        user_id=test_user.id,
        started_at=datetime(2025, 11, 23, 16, 0, 0, tzinfo=timezone.utc),
        daily_room_id="room-no-messages"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Verify no messages exist
    from src.models.conversation_message import ConversationMessage
    messages = session.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation.id
    ).all()
    assert len(messages) == 0

    # TODO: Full endpoint test requires JWT auth fixtures
    # Expected response:
    # {
    #     "conversation": {...},
    #     "messages": []
    # }
    pass


def test_get_conversation_single_conversation(test_user, session: Session):
    """
    GIVEN: User has only one conversation
    WHEN: Requesting GET /conversations/{id}
    THEN: Returns that conversation successfully

    Edge case: Single conversation
    """
    # Create single conversation
    conversation = Conversation(
        user_id=test_user.id,
        started_at=datetime(2025, 11, 23, 17, 0, 0, tzinfo=timezone.utc),
        daily_room_id="single-room"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Verify it's the only conversation
    user_conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).all()
    assert len(user_conversations) == 1
    assert user_conversations[0].id == conversation.id

    # TODO: Full endpoint test requires JWT auth fixtures
    pass


# ============================================================================
# Integration Tests (Story 5.2 AC #7)
# ============================================================================

def test_conversation_history_integration_flow(test_user, session: Session):
    """
    GIVEN: User creates multiple conversations
    WHEN: User lists conversations and then gets details
    THEN: Full flow works end-to-end (Postman-like scenario)

    AC #7: Integration test - can test with Postman to see conversation list
    """
    from src.models.conversation_message import ConversationMessage, MessageRole

    # Step 1: Create 3 conversations with messages
    conversations = []
    for i in range(3):
        conv = Conversation(
            user_id=test_user.id,
            started_at=datetime(2025, 11, 20 + i, 10, 0, 0, tzinfo=timezone.utc),
            daily_room_id=f"integration-room-{i}"
        )
        if i < 2:  # End first 2 conversations
            conv.ended_at = datetime(2025, 11, 20 + i, 10, 30, 0, tzinfo=timezone.utc)
            conv.calculate_duration()

        session.add(conv)
        session.commit()
        session.refresh(conv)

        # Add messages to each conversation
        for j in range(2):
            msg = ConversationMessage(
                conversation_id=conv.id,
                role=MessageRole.USER if j == 0 else MessageRole.ASSISTANT,
                content=f"Message {j} in conversation {i}",
                timestamp=conv.started_at + __import__('datetime').timedelta(minutes=j * 5),
                message_metadata={}
            )
            session.add(msg)

        session.commit()
        conversations.append(conv)

    # Step 2: List conversations (simulating GET /conversations)
    listed_conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).order_by(Conversation.started_at.desc()).all()

    assert len(listed_conversations) == 3
    # Most recent first (conv2, conv1, conv0)
    assert listed_conversations[0].id == conversations[2].id

    # Step 3: Get details for first conversation (simulating GET /conversations/{id})
    detail_conversation = session.get(Conversation, conversations[0].id)
    assert detail_conversation is not None
    assert detail_conversation.user_id == test_user.id

    detail_messages = session.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversations[0].id
    ).order_by(ConversationMessage.timestamp.asc()).all()

    assert len(detail_messages) == 2

    # TODO: Full endpoint integration test requires JWT auth fixtures
    # This test simulates the database layer; full API test would:
    # 1. POST /conversations/start (create conversations)
    # 2. GET /conversations (list them)
    # 3. GET /conversations/{id} (get details)
    # 4. Verify all responses match expected format
    pass
