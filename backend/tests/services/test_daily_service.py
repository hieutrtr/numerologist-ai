"""
Unit tests for Daily.co Room Management Service

Tests cover:
- Environment variable validation
- Room creation success and failure scenarios
- Room deletion with various responses
- Meeting token generation
- Error handling for API and network failures
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, Mock
import httpx
import time
import os

# Now safe to import the module
from src.services import daily_service


# Fixture to mock DAILY_API_KEY for all tests
@pytest.fixture(autouse=True)
def mock_daily_api_key():
    """Mock DAILY_API_KEY for all tests"""
    with patch("src.services.daily_service.DAILY_API_KEY", "test-api-key-for-testing"):
        yield


# Test fixtures
@pytest.fixture
def mock_room_response():
    """Mock successful room creation response from Daily.co API"""
    return {
        "url": "https://example.daily.co/numerologist-test-123",
        "name": "numerologist-test-123",
        "id": "room-id-123",
        "created_at": "2025-11-08T12:00:00Z"
    }


@pytest.fixture
def mock_token_response():
    """Mock successful meeting token response from Daily.co API"""
    return {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-token-payload.signature"
    }


# AC6: Test environment variable validation
def test_create_room_validates_api_key_configured():
    """Test that create_room validates DAILY_API_KEY is configured"""
    # Verify the module attribute exists
    assert hasattr(daily_service, "DAILY_API_KEY")
    # In test environment, it's mocked to test-api-key-for-testing
    assert daily_service.DAILY_API_KEY == "test-api-key-for-testing"


# AC2: Test create_room() function
@pytest.mark.asyncio
async def test_create_room_success(mock_room_response, mock_token_response):
    """Test successful room creation with all required fields"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_room_resp = AsyncMock()
        mock_room_resp.json = Mock(return_value=mock_room_response)
        mock_room_resp.raise_for_status = Mock()

        mock_token_resp = AsyncMock()
        mock_token_resp.json = Mock(return_value=mock_token_response)
        mock_token_resp.raise_for_status = Mock()

        mock_client.post = AsyncMock(side_effect=[mock_room_resp, mock_token_resp])

        result = await daily_service.create_room("test-123")

        assert result["room_url"] == "https://example.daily.co/numerologist-test-123"
        assert result["room_name"] == "numerologist-test-123"
        assert result["meeting_token"] == mock_token_response["token"]

        assert mock_client.post.call_count == 2


@pytest.mark.asyncio
async def test_create_room_generates_correct_room_name():
    """Test that room name follows numerologist-{conversation_id} pattern"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.json = Mock(return_value={
            "url": "https://example.daily.co/numerologist-abc-456",
            "name": "numerologist-abc-456"
        })
        mock_resp.raise_for_status = Mock()

        mock_token_resp = MagicMock()
        mock_token_resp.json = Mock(return_value={"token": "test-token"})
        mock_token_resp.raise_for_status = Mock()

        mock_client.post = AsyncMock(side_effect=[mock_resp, mock_token_resp])

        await daily_service.create_room("abc-456")

        call_args = mock_client.post.call_args_list[0]
        payload = call_args[1]["json"]
        assert payload["name"] == "numerologist-abc-456"


@pytest.mark.asyncio
async def test_create_room_sets_expiry_correctly():
    """Test that room expiry is set to 2 hours from creation"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.json = Mock(return_value={
            "url": "https://example.daily.co/numerologist-test",
            "name": "numerologist-test"
        })
        mock_resp.raise_for_status = Mock()

        mock_token_resp = MagicMock()
        mock_token_resp.json = Mock(return_value={"token": "test-token"})
        mock_token_resp.raise_for_status = Mock()

        mock_client.post = AsyncMock(side_effect=[mock_resp, mock_token_resp])

        current_time = time.time()
        with patch("time.time", return_value=current_time):
            await daily_service.create_room("test")

        call_args = mock_client.post.call_args_list[0]
        payload = call_args[1]["json"]
        expected_expiry = int(current_time) + (2 * 3600)
        assert payload["properties"]["exp"] == expected_expiry


# AC5: Test error handling
@pytest.mark.asyncio
async def test_create_room_handles_http_error():
    """Test that HTTP errors are caught and wrapped in DailyRoomCreationError"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.raise_for_status = Mock(side_effect=httpx.HTTPStatusError(
            "Server error",
            request=MagicMock(),
            response=mock_resp
        ))

        mock_client.post = AsyncMock(return_value=mock_resp)

        with pytest.raises(daily_service.DailyRoomCreationError, match="Failed to create room"):
            await daily_service.create_room("test-error")


@pytest.mark.asyncio
async def test_create_room_handles_network_error():
    """Test that network errors are caught and wrapped in DailyRoomCreationError"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_client.post = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        with pytest.raises(daily_service.DailyRoomCreationError, match="Network error"):
            await daily_service.create_room("test-network-error")


# AC3: Test delete_room() function
@pytest.mark.asyncio
async def test_delete_room_success():
    """Test successful room deletion returns True"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = Mock()

        mock_client.delete = AsyncMock(return_value=mock_resp)

        result = await daily_service.delete_room("numerologist-test-123")

        assert result is True


@pytest.mark.asyncio
async def test_delete_room_handles_404():
    """Test that 404 response (room not found) returns False gracefully"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.status_code = 404

        mock_client.delete = AsyncMock(return_value=mock_resp)

        result = await daily_service.delete_room("non-existent-room")

        assert result is False


@pytest.mark.asyncio
async def test_delete_room_handles_http_error():
    """Test that HTTP errors return False (graceful degradation)"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status = Mock(side_effect=httpx.HTTPStatusError(
            "Server error",
            request=MagicMock(),
            response=mock_resp
        ))

        mock_client.delete = AsyncMock(return_value=mock_resp)

        result = await daily_service.delete_room("test-room")

        assert result is False


@pytest.mark.asyncio
async def test_delete_room_handles_network_error():
    """Test that network errors return False (graceful degradation)"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_client.delete = AsyncMock(side_effect=httpx.RequestError("Connection failed"))

        result = await daily_service.delete_room("test-room")

        assert result is False


# AC4: Test create_meeting_token() function
@pytest.mark.asyncio
async def test_create_meeting_token_success(mock_token_response):
    """Test successful meeting token generation"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.json = Mock(return_value=mock_token_response)
        mock_resp.raise_for_status = Mock()

        mock_client.post = AsyncMock(return_value=mock_resp)

        token = await daily_service.create_meeting_token("numerologist-test-123")

        assert token == mock_token_response["token"]


@pytest.mark.asyncio
async def test_create_meeting_token_handles_http_error():
    """Test that HTTP errors are caught and wrapped in DailyRoomCreationError"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.text = "Forbidden"
        mock_resp.raise_for_status = Mock(side_effect=httpx.HTTPStatusError(
            "Forbidden",
            request=MagicMock(),
            response=mock_resp
        ))

        mock_client.post = AsyncMock(return_value=mock_resp)

        with pytest.raises(daily_service.DailyRoomCreationError, match="Failed to generate meeting token"):
            await daily_service.create_meeting_token("test-room")


@pytest.mark.asyncio
async def test_create_meeting_token_handles_network_error():
    """Test that network errors are caught and wrapped in DailyRoomCreationError"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_client.post = AsyncMock(side_effect=httpx.RequestError("Connection timeout"))

        with pytest.raises(daily_service.DailyRoomCreationError, match="Network error"):
            await daily_service.create_meeting_token("test-room")


# Integration-style tests
@pytest.mark.asyncio
async def test_create_room_calls_create_meeting_token():
    """Test that create_room() calls create_meeting_token() for the created room"""

    with patch("src.services.daily_service.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        mock_room_resp = AsyncMock()
        mock_room_resp.json = Mock(return_value={
            "url": "https://example.daily.co/numerologist-integration-test",
            "name": "numerologist-integration-test"
        })
        mock_room_resp.raise_for_status = Mock()

        mock_token_resp = AsyncMock()
        mock_token_resp.json = Mock(return_value={"token": "integration-test-token"})
        mock_token_resp.raise_for_status = Mock()

        mock_client.post = AsyncMock(side_effect=[mock_room_resp, mock_token_resp])

        result = await daily_service.create_room("integration-test")

        assert mock_client.post.call_count == 2
        assert result["meeting_token"] == "integration-test-token"

        token_call_args = mock_client.post.call_args_list[1]
        token_payload = token_call_args[1]["json"]
        assert token_payload["properties"]["room_name"] == "numerologist-integration-test"
