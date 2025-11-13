"""
Conversation Endpoints - TEMPLATE

API endpoints for managing voice conversations. Customize based on your
authentication and database requirements.

Endpoints:
- POST /conversations/start - Create new conversation and spawn bot
- POST /conversations/{id}/end - End conversation and cleanup
"""

import asyncio
import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status

# TODO: Import your authentication dependencies
# from core.deps import get_current_user
# from models.user import User

from services.daily_service import create_room, delete_room
from voice_pipeline.pipecat_bot import run_bot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_conversation(
    # TODO: Add authentication
    # current_user: User = Depends(get_current_user),
) -> dict:
    """
    Start a new voice conversation.

    Creates a Daily.co room and spawns the voice bot in the background.

    Returns:
        dict with conversation_id, daily_room_url, and daily_token

    Raises:
        HTTPException 500: If room creation or bot spawn fails

    Example:
        >>> response = await start_conversation()
        >>> print(response["daily_room_url"])
    """
    try:
        # Generate unique conversation ID
        conversation_id = str(uuid4())

        logger.info(f"Creating conversation: {conversation_id}")

        # Create Daily.co room
        logger.info(f"Creating Daily.co room for conversation {conversation_id}")
        room_data = await create_room(conversation_id)

        logger.info(f"Created Daily.co room: {room_data['room_name']}")

        # Spawn bot in background (non-blocking)
        logger.info(f"Spawning voice bot for conversation {conversation_id}")

        # TODO: Pass user data for personalization
        user_data = None  # Replace with: {"name": current_user.name, ...}

        asyncio.create_task(
            run_bot(
                room_data["room_url"],
                room_data["meeting_token"],
                user_data
            )
        )

        logger.info(f"Bot spawned for conversation {conversation_id}")

        # Return room details to client
        return {
            "conversation_id": conversation_id,
            "daily_room_url": room_data["room_url"],
            "daily_token": room_data["meeting_token"]
        }

    except Exception as e:
        logger.error(
            f"Failed to start conversation: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start conversation: {str(e)}"
        ) from e


@router.post("/{conversation_id}/end", status_code=status.HTTP_200_OK)
async def end_conversation(
    conversation_id: str,
    # TODO: Add authentication
    # current_user: User = Depends(get_current_user),
) -> dict:
    """
    End a voice conversation and cleanup resources.

    Performs best-effort cleanup of the Daily.co room.

    Args:
        conversation_id: UUID of the conversation to end

    Returns:
        dict with success message and conversation details

    Raises:
        HTTPException 404: If conversation not found

    Example:
        >>> response = await end_conversation("550e8400-...")
        >>> print(response["message"])
    """
    try:
        logger.info(f"Ending conversation {conversation_id}")

        # TODO: Add database lookup and validation
        # conversation = session.get(Conversation, conversation_id)
        # if not conversation:
        #     raise HTTPException(404, "Conversation not found")
        # if conversation.user_id != current_user.id:
        #     raise HTTPException(403, "Not authorized")

        # Best-effort cleanup of Daily.co room
        # Rooms auto-expire, so this isn't critical
        try:
            deleted = await delete_room(conversation_id)
            if deleted:
                logger.info(f"Successfully deleted Daily.co room: {conversation_id}")
            else:
                logger.warning(
                    f"Daily.co room deletion returned False for: {conversation_id}"
                )
        except Exception as room_error:
            # Log but don't fail - rooms auto-expire
            logger.error(
                f"Failed to delete Daily.co room {conversation_id}: {str(room_error)}",
                exc_info=True
            )
            logger.info("Continuing despite cleanup failure (rooms auto-expire)")

        return {
            "message": "Conversation ended successfully",
            "conversation_id": conversation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error ending conversation {conversation_id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end conversation: {str(e)}"
        ) from e


# =============================================================================
# IMPLEMENTATION NOTES
# =============================================================================

"""
Customization Checklist:

1. Authentication:
   - Add get_current_user dependency
   - Create User model
   - Implement JWT verification

2. Database:
   - Create Conversation model
   - Store conversation records
   - Track started_at, ended_at, duration

3. Authorization:
   - Validate conversation belongs to user
   - Add permission checks

4. Rate Limiting:
   - Limit conversations per user
   - Prevent abuse

5. Monitoring:
   - Log conversation metrics
   - Track errors and latency

Example with Database:

```python
from sqlmodel import Session, select
from models.conversation import Conversation

@router.post("/start")
async def start_conversation(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Create conversation record
    conversation = Conversation(user_id=current_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create room
    room_data = await create_room(str(conversation.id))

    # Update with room ID
    conversation.daily_room_id = room_data["room_name"]
    session.commit()

    # Spawn bot with user context
    asyncio.create_task(
        run_bot(room_data["room_url"], room_data["meeting_token"], current_user)
    )

    return {
        "conversation_id": str(conversation.id),
        "daily_room_url": room_data["room_url"],
        "daily_token": room_data["meeting_token"]
    }
```
"""
