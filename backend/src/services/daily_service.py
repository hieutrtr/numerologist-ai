"""
Daily.co Room Management Service

This module provides async functions to create and manage Daily.co WebRTC rooms
for voice conversations in the Numerologist AI application.

Daily.co provides managed WebRTC infrastructure with reliable mobile support
and native Pipecat-ai integration, enabling real-time voice interactions between
users and the AI numerologist.

Environment Variables Required:
    DAILY_API_KEY: API key for Daily.co REST API
        Get from: https://dashboard.daily.co/ → Developers → API Keys
        See: backend/.env.example for setup instructions

API Documentation:
    Daily.co REST API: https://docs.daily.co/reference/rest-api
    Daily.co Python SDK: https://docs.daily.co/reference/daily-python

Usage Example:
    from src.services import daily_service

    # Create a room for a conversation
    room_info = await daily_service.create_room("conversation-123")
    print(f"Room URL: {room_info['room_url']}")
    print(f"Meeting Token: {room_info['meeting_token']}")

    # Later, cleanup the room
    deleted = await daily_service.delete_room(room_info['room_name'])
"""

import time
import httpx
from typing import Dict
import logging

from src.core.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DAILY_API_URL = "https://api.daily.co/v1"
"""Base URL for Daily.co REST API v1"""

ROOM_EXPIRY_HOURS = 2
"""Room expiry time in hours (balances security and user experience)"""

# Load API key from settings (lazy validation - checked when functions are called)
DAILY_API_KEY = settings.daily_api_key


# Custom exceptions
class DailyRoomCreationError(Exception):
    """
    Raised when Daily.co room creation or management fails.

    This exception wraps HTTP errors and network errors from the Daily.co API,
    providing a consistent error interface for the application.
    """
    pass


async def create_room(conversation_id: str) -> Dict[str, str]:
    """
    Create a Daily.co room for a voice conversation.

    This function creates a new Daily.co WebRTC room with a unique name based on
    the conversation ID, sets appropriate room properties (2-hour expiry, voice-only),
    and generates a meeting token for secure client access.

    Args:
        conversation_id: Unique identifier for the conversation.
            Used to generate room name: "numerologist-{conversation_id}"

    Returns:
        Dict containing:
            - room_url (str): Full URL to the Daily.co room
            - room_name (str): Unique room identifier
            - meeting_token (str): JWT token for secure room access

    Raises:
        DailyRoomCreationError: If room creation fails due to API error or network issue

    Example:
        >>> room = await create_room("abc-123")
        >>> print(room['room_url'])
        'https://example.daily.co/numerologist-abc-123'
        >>> print(room['meeting_token'][:20])
        'eyJhbGciOiJIUzI1NiIs...'
    """
    if not DAILY_API_KEY:
        raise ValueError(
            "DAILY_API_KEY is not configured. "
            "Set the DAILY_API_KEY environment variable or add it to .env file. "
            "Get your API key from: https://dashboard.daily.co/ "
            "See backend/.env.example for setup instructions."
        )

    room_name = f"numerologist-{conversation_id}"
    expiry = int(time.time()) + (ROOM_EXPIRY_HOURS * 3600)

    headers = {
        "Authorization": f"Bearer {DAILY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": room_name,
        "properties": {
            "exp": expiry,
            "enable_chat": False,
            "enable_screenshare": False
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            # Create room
            logger.info(f"Creating Daily.co room: {room_name}")
            response = await client.post(
                f"{DAILY_API_URL}/rooms",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            room_data = response.json()
            logger.info(f"Room created successfully: {room_data['url']}")

            # Generate meeting token
            meeting_token = await create_meeting_token(room_name)

            return {
                "room_url": room_data["url"],
                "room_name": room_data["name"],
                "meeting_token": meeting_token
            }

    except httpx.HTTPStatusError as e:
        error_msg = f"Daily API error: {e.response.status_code}"
        logger.error(f"{error_msg} - {e.response.text}", exc_info=True)
        raise DailyRoomCreationError(
            f"Failed to create room '{room_name}': HTTP {e.response.status_code}"
        ) from e
    except httpx.RequestError as e:
        error_msg = f"Network error creating room '{room_name}'"
        logger.error(error_msg, exc_info=True)
        raise DailyRoomCreationError(
            f"Network error creating room: {str(e)}"
        ) from e


async def delete_room(room_name: str) -> bool:
    """
    Delete a Daily.co room.

    Used for conversation cleanup. Handles 404 errors gracefully (room already
    deleted or expired).

    Args:
        room_name: Name of the room to delete (e.g., "numerologist-abc-123")

    Returns:
        True if room was deleted successfully, False if room not found or deletion failed

    Example:
        >>> deleted = await delete_room("numerologist-abc-123")
        >>> print(deleted)
        True
    """
    headers = {
        "Authorization": f"Bearer {DAILY_API_KEY}",
    }

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"Deleting Daily.co room: {room_name}")
            response = await client.delete(
                f"{DAILY_API_URL}/rooms/{room_name}",
                headers=headers,
                timeout=10.0
            )

            # Handle 404 gracefully (room already deleted or expired)
            if response.status_code == 404:
                logger.warning(f"Room not found (already deleted?): {room_name}")
                return False

            response.raise_for_status()
            logger.info(f"Room deleted successfully: {room_name}")
            return True

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Daily API error deleting room '{room_name}': {e.response.status_code}",
            exc_info=True
        )
        return False
    except httpx.RequestError as e:
        logger.error(f"Network error deleting room '{room_name}'", exc_info=True)
        return False


async def create_meeting_token(room_name: str) -> str:
    """
    Generate a meeting token for secure room access.

    Meeting tokens allow clients to join rooms without exposing the API key.
    Tokens are scoped to a specific room.

    Args:
        room_name: Name of the room for which to generate a token

    Returns:
        JWT meeting token string

    Raises:
        DailyRoomCreationError: If token generation fails

    Example:
        >>> token = await create_meeting_token("numerologist-abc-123")
        >>> print(token[:20])
        'eyJhbGciOiJIUzI1NiIs...'
    """
    headers = {
        "Authorization": f"Bearer {DAILY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "properties": {
            "room_name": room_name
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            logger.debug(f"Generating meeting token for room: {room_name}")
            response = await client.post(
                f"{DAILY_API_URL}/meeting-tokens",
                json=payload,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            token_data = response.json()
            logger.debug(f"Meeting token generated for room: {room_name}")
            return token_data["token"]

    except httpx.HTTPStatusError as e:
        error_msg = f"Daily API error generating token: {e.response.status_code}"
        logger.error(f"{error_msg} - {e.response.text}", exc_info=True)
        raise DailyRoomCreationError(
            f"Failed to generate meeting token for room '{room_name}': HTTP {e.response.status_code}"
        ) from e
    except httpx.RequestError as e:
        error_msg = f"Network error generating token for room '{room_name}'"
        logger.error(error_msg, exc_info=True)
        raise DailyRoomCreationError(
            f"Network error generating token: {str(e)}"
        ) from e


# Manual testing examples (curl commands)
"""
Manual API Testing with curl:

1. Create a room:
   curl -X POST https://api.daily.co/v1/rooms \
     -H "Authorization: Bearer YOUR_DAILY_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "test-room-001",
       "properties": {
         "exp": 1699999999,
         "enable_chat": false,
         "enable_screenshare": false
       }
     }'

2. List rooms:
   curl https://api.daily.co/v1/rooms \
     -H "Authorization: Bearer YOUR_DAILY_API_KEY"

3. Generate meeting token:
   curl -X POST https://api.daily.co/v1/meeting-tokens \
     -H "Authorization: Bearer YOUR_DAILY_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"properties": {"room_name": "test-room-001"}}'

4. Delete a room:
   curl -X DELETE https://api.daily.co/v1/rooms/test-room-001 \
     -H "Authorization: Bearer YOUR_DAILY_API_KEY"
"""
