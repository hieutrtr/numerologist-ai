"""
Conversation Endpoints

API endpoints for voice conversation management including conversation creation,
room setup, and bot initialization.
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.models.conversation import Conversation
from src.models.user import User
from src.services.daily_service import create_room
from src.voice_pipeline.pipecat_bot import run_bot
from src.core.deps import get_current_user
from src.core.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_conversation(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> dict:
    """
    Start a new voice conversation.

    Creates a new conversation record, establishes a Daily.co WebRTC room,
    and spawns the Pipecat AI bot in the background.

    The endpoint returns the conversation ID, Daily.co room URL, and meeting token
    to the client, which can then join the room and interact with the bot.

    Args:
        current_user: Authenticated user (from JWT token)
        session: Database session for recording the conversation

    Returns:
        dict: Response with conversation details:
            {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "daily_room_url": "https://domain.daily.co/room-name",
                "daily_token": "eyJhbGciOiJIUzI1NiIs..."
            }

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If Daily.co room creation or bot spawn fails

    Implementation Details:
        1. Create Conversation record in database with user_id
        2. Generate unique conversation_id (UUID)
        3. Call daily_service.create_room() to get WebRTC room details
        4. Update conversation with daily_room_id
        5. Commit database transaction
        6. Spawn pipecat_bot.run_bot() as background task (non-blocking)
        7. Return conversation details to client

    Security:
        - Endpoint requires valid JWT authentication (get_current_user)
        - Conversation associated with authenticated user
        - Daily.co tokens are short-lived and room-specific

    Background Processing:
        - Bot initialization happens asynchronously
        - Errors in bot startup don't block endpoint response
        - Bot errors are logged for monitoring/debugging
    """
    try:
        # Step 1: Create Conversation record
        logger.info(f"Creating conversation for user {current_user.id}")
        conversation = Conversation(user_id=current_user.id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {current_user.id}")

        # Step 2: Create Daily.co room
        logger.info(f"Creating Daily.co room for conversation {conversation.id}")
        room_data = await create_room(str(conversation.id))

        # Step 3: Update conversation with room ID
        conversation.daily_room_id = room_data["room_name"]
        session.commit()

        logger.info(f"Created Daily.co room: {room_data['room_name']}")

        # Step 4: Spawn bot in background (non-blocking)
        logger.info(f"Spawning Pipecat bot for conversation {conversation.id}")
        asyncio.create_task(
            run_bot(room_data["room_url"], room_data["meeting_token"])
        )

        logger.info(f"Bot spawned for conversation {conversation.id}")

        # Step 5: Return response to client
        return {
            "conversation_id": str(conversation.id),
            "daily_room_url": room_data["room_url"],
            "daily_token": room_data["meeting_token"]
        }

    except Exception as e:
        # Log error with full context for debugging
        logger.error(
            f"Failed to start conversation for user {current_user.id}: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        # Rollback any pending database changes
        session.rollback()
        # Return 500 server error with descriptive message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start conversation: {str(e)}"
        ) from e
