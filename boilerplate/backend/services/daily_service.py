"""
Daily.co Room Management Service

Provides functions for creating and managing Daily.co WebRTC rooms
for voice conversations.

Documentation: https://docs.daily.co/reference/rest-api
"""

import logging
import httpx
from typing import Dict, Optional
from core.settings import settings

logger = logging.getLogger(__name__)

DAILY_API_URL = "https://api.daily.co/v1"


async def create_room(room_name: str, expiry_minutes: int = 120) -> Dict[str, str]:
    """
    Create a Daily.co room for voice conversation.

    Args:
        room_name: Unique identifier for the room (e.g., conversation ID)
        expiry_minutes: Room auto-deletion time (default: 2 hours)

    Returns:
        dict containing:
            - room_url: URL to join the room
            - room_name: Created room identifier
            - meeting_token: JWT token for secure access

    Raises:
        httpx.HTTPError: If room creation fails

    Example:
        >>> room = await create_room("conversation-123")
        >>> print(room["room_url"])
        https://your-domain.daily.co/conversation-123
    """
    try:
        logger.info(f"Creating Daily.co room: {room_name}")

        async with httpx.AsyncClient() as client:
            # Create room
            response = await client.post(
                f"{DAILY_API_URL}/rooms",
                headers={
                    "Authorization": f"Bearer {settings.daily_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "name": room_name,
                    "properties": {
                        "exp": expiry_minutes * 60,  # Convert to seconds
                        "enable_screenshare": False,
                        "enable_chat": False,
                        "enable_recording": False,  # TODO: Enable if needed
                    },
                },
                timeout=30.0,
            )
            response.raise_for_status()
            room_data = response.json()

            logger.info(f"Room created successfully: {room_name}")

            # Create meeting token for secure access
            token_response = await client.post(
                f"{DAILY_API_URL}/meeting-tokens",
                headers={
                    "Authorization": f"Bearer {settings.daily_api_key}",
                    "Content-Type": "application/json",
                },
                json={"properties": {"room_name": room_name}},
                timeout=30.0,
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            return {
                "room_url": room_data["url"],
                "room_name": room_data["name"],
                "meeting_token": token_data["token"],
            }

    except httpx.HTTPError as e:
        logger.error(f"Failed to create Daily.co room: {e}", exc_info=True)
        raise


async def delete_room(room_name: str) -> bool:
    """
    Delete a Daily.co room (best-effort cleanup).

    Rooms auto-expire after the configured time, so this is not critical.
    Errors are logged but don't fail the operation.

    Args:
        room_name: Room identifier to delete

    Returns:
        True if deleted successfully, False otherwise

    Example:
        >>> deleted = await delete_room("conversation-123")
    """
    try:
        logger.info(f"Deleting Daily.co room: {room_name}")

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{DAILY_API_URL}/rooms/{room_name}",
                headers={"Authorization": f"Bearer {settings.daily_api_key}"},
                timeout=30.0,
            )
            response.raise_for_status()

            logger.info(f"Room deleted successfully: {room_name}")
            return True

    except httpx.HTTPError as e:
        logger.warning(
            f"Failed to delete Daily.co room {room_name}: {e}. "
            "Room will auto-expire."
        )
        return False


async def get_room_info(room_name: str) -> Optional[Dict]:
    """
    Get information about an existing Daily.co room.

    Args:
        room_name: Room identifier

    Returns:
        Room information dict or None if not found

    Example:
        >>> info = await get_room_info("conversation-123")
        >>> print(info["created_at"])
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DAILY_API_URL}/rooms/{room_name}",
                headers={"Authorization": f"Bearer {settings.daily_api_key}"},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"Failed to get room info for {room_name}: {e}")
        return None
