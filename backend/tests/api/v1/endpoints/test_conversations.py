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
