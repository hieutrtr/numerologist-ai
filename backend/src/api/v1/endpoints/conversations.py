"""
Conversation Endpoints

API endpoints for voice conversation management including conversation creation,
room setup, and bot initialization.
"""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.models.conversation import Conversation
from src.models.user import User
from src.services.daily_service import create_room, delete_room
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


@router.post("/{conversation_id}/end", status_code=status.HTTP_200_OK)
async def end_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> dict:
    """
    End a voice conversation and cleanup resources.

    Marks the conversation as ended, calculates duration, and deletes the Daily.co room.
    This endpoint performs best-effort cleanup - it continues even if Daily.co deletion fails
    since rooms auto-expire anyway.

    Args:
        conversation_id: UUID of the conversation to end
        current_user: Authenticated user (from JWT token)
        session: Database session for updating the conversation

    Returns:
        dict: Response with conversation details:
            {
                "message": "Conversation ended successfully",
                "conversation": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "started_at": "2025-11-10T14:00:00Z",
                    "ended_at": "2025-11-10T14:15:00Z",
                    "duration_seconds": 900
                }
            }

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 403: If conversation does not belong to user
        HTTPException 404: If conversation not found
        HTTPException 400: If conversation is already ended

    Implementation Details:
        1. Query conversation by ID from database
        2. Validate conversation exists and belongs to current user
        3. Check if conversation is already ended
        4. Update ended_at timestamp and calculate duration
        5. Commit database changes
        6. Attempt to delete Daily.co room (best-effort, don't fail if this fails)
        7. Return conversation details

    Security:
        - Endpoint requires valid JWT authentication (get_current_user)
        - Validates conversation ownership before allowing end operation
        - Returns 403 if user tries to end another user's conversation

    Graceful Degradation:
        - If Daily.co room deletion fails, the operation still succeeds
        - Rooms auto-expire after 2 hours, so cleanup is not critical
        - Errors are logged for monitoring but don't block the user
    """
    try:
        # Step 1: Query conversation by ID
        logger.info(f"Attempting to end conversation {conversation_id} for user {current_user.id}")
        conversation = session.get(Conversation, conversation_id)

        # Step 2: Validate conversation exists
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Step 3: Validate conversation belongs to current user
        if conversation.user_id != current_user.id:
            logger.warning(
                f"User {current_user.id} attempted to end conversation {conversation_id} "
                f"owned by user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to end this conversation"
            )

        # Step 4: Check if conversation is already ended
        if conversation.ended_at:
            logger.warning(f"Conversation {conversation_id} is already ended")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Conversation already ended"
            )

        # Step 5: Update conversation with ended_at and calculate duration
        conversation.ended_at = datetime.now(timezone.utc)
        conversation.calculate_duration()  # Uses helper method from model
        session.commit()
        session.refresh(conversation)

        logger.info(
            f"Conversation {conversation_id} ended successfully. "
            f"Duration: {conversation.duration_seconds} seconds"
        )

        # Step 6: Attempt to delete Daily.co room (best-effort)
        # NOTE: This may cause WebSocket cleanup warnings from the bot since we're deleting
        # the room while the bot is still connected. These warnings are expected and harmless:
        # - "failed to send message on WebSocket: Protocol(SendAfterClosing)"
        # - "Failed to send logs on disconnect"
        # The bot's WebSocket connection closes when the room is deleted, and the bot
        # tries to send cleanup messages on the already-closed connection.
        # Future improvement: Implement proper bot lifecycle management to gracefully
        # shutdown the bot before deleting the room.
        if conversation.daily_room_id:
            try:
                deleted = await delete_room(conversation.daily_room_id)
                if deleted:
                    logger.info(f"Successfully deleted Daily.co room: {conversation.daily_room_id}")
                else:
                    logger.warning(
                        f"Daily.co room deletion returned False for: {conversation.daily_room_id}. "
                        "Room may have already been deleted or expired."
                    )
            except Exception as room_error:
                # Log the error but don't fail the endpoint
                # Daily.co rooms auto-expire, so cleanup is not critical
                logger.error(
                    f"Failed to delete Daily.co room {conversation.daily_room_id}: {str(room_error)}",
                    exc_info=True
                )
                logger.info("Continuing despite Daily.co cleanup failure (rooms auto-expire)")

        # Step 7: Return success response with conversation details
        return {
            "message": "Conversation ended successfully",
            "conversation": {
                "id": str(conversation.id),
                "started_at": conversation.started_at.isoformat(),
                "ended_at": conversation.ended_at.isoformat(),
                "duration_seconds": conversation.duration_seconds
            }
        }

    except HTTPException:
        # Re-raise HTTP exceptions (404, 400, 403) as-is
        raise
    except Exception as e:
        # Log unexpected errors with full context
        logger.error(
            f"Unexpected error ending conversation {conversation_id} for user {current_user.id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        # Rollback any pending database changes
        session.rollback()
        # Return 500 server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end conversation: {str(e)}"
        ) from e
