"""
Conversation Endpoints

API endpoints for voice conversation management including conversation creation,
room setup, and bot initialization.
"""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.models.conversation import Conversation
from src.models.conversation_message import ConversationMessage, MessageRole
from src.models.user import User
from src.services.daily_service import create_room, delete_room
from src.voice_pipeline.pipecat_bot import run_bot
from src.core.deps import get_current_user
from src.core.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


# Response schemas
class MessageResponse(BaseModel):
    """Schema for conversation message response."""
    id: str
    role: str
    content: str
    timestamp: str
    message_metadata: dict

    model_config = ConfigDict(from_attributes=True)


class ConversationMessagesResponse(BaseModel):
    """Schema for paginated conversation messages response."""
    conversation_id: str
    messages: List[MessageResponse]
    total: int
    page: int
    limit: int
    has_more: bool


class ConversationSummary(BaseModel):
    """Schema for conversation summary in list view."""
    id: str
    started_at: str
    ended_at: Optional[str]
    duration: Optional[int]
    main_topic: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list response."""
    conversations: List[ConversationSummary]
    total: int
    page: int
    limit: int
    has_more: bool


class ConversationDetailResponse(BaseModel):
    """Schema for conversation detail with messages."""
    conversation: ConversationSummary
    messages: List[MessageResponse]


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
) -> ConversationListResponse:
    """
    List user's conversations with pagination.

    Returns a paginated list of conversations ordered by most recent first.
    Each conversation includes id, timing information, and optional main topic.

    Args:
        current_user: Authenticated user (from JWT token)
        session: Database session
        page: Page number (default: 1)
        limit: Items per page (default: 20, max: 100)

    Returns:
        ConversationListResponse: Paginated conversations with metadata:
            {
                "conversations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "started_at": "2025-11-23T14:00:00Z",
                        "ended_at": "2025-11-23T14:15:00Z",
                        "duration": 900,
                        "main_topic": "Life Path Number"
                    },
                    ...
                ],
                "total": 45,
                "page": 1,
                "limit": 20,
                "has_more": true
            }

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 422: If page or limit parameters are invalid

    Implementation Details:
        1. Query conversations filtered by user_id
        2. Order by started_at descending (most recent first)
        3. Apply pagination (LIMIT/OFFSET)
        4. Count total conversations for pagination metadata
        5. Calculate has_more flag based on total and current page

    Security:
        - Endpoint requires valid JWT authentication
        - Only returns conversations owned by current user
    """
    try:
        logger.info(f"Listing conversations for user {current_user.id}, page {page}")

        # Count total conversations for user
        total_count_stmt = (
            select(func.count())
            .select_from(Conversation)
            .where(Conversation.user_id == current_user.id)
        )
        total = session.exec(total_count_stmt).one()

        # Query conversations with pagination
        offset = (page - 1) * limit
        query = (
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.started_at.desc())
            .offset(offset)
            .limit(limit)
        )
        conversations = session.exec(query).all()

        # Format response
        conversation_summaries = [
            ConversationSummary(
                id=str(conv.id),
                started_at=conv.started_at.isoformat(),
                ended_at=conv.ended_at.isoformat() if conv.ended_at else None,
                duration=conv.duration_seconds,
                main_topic=conv.main_topic  # Populated by end_conversation
            )
            for conv in conversations
        ]

        has_more = (offset + len(conversations)) < total

        logger.info(
            f"Retrieved {len(conversations)} conversations for user {current_user.id}, "
            f"page {page} (total: {total})"
        )

        return ConversationListResponse(
            conversations=conversation_summaries,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more
        )

    except Exception as e:
        logger.error(
            f"Unexpected error listing conversations for user {current_user.id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {str(e)}"
        ) from e


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ConversationDetailResponse:
    """
    Get full conversation with all messages.

    Retrieves a specific conversation including all messages ordered by timestamp.
    Requires user to own the conversation.

    Args:
        conversation_id: UUID of the conversation
        current_user: Authenticated user (from JWT token)
        session: Database session

    Returns:
        ConversationDetailResponse: Conversation with messages:
            {
                "conversation": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "started_at": "2025-11-23T14:00:00Z",
                    "ended_at": "2025-11-23T14:15:00Z",
                    "duration": 900,
                    "main_topic": "Life Path Number"
                },
                "messages": [
                    {
                        "id": "...",
                        "role": "user",
                        "content": "What's my life path number?",
                        "timestamp": "2025-11-23T14:00:00Z",
                        "message_metadata": {}
                    },
                    ...
                ]
            }

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 403: If conversation does not belong to user
        HTTPException 404: If conversation not found

    Implementation Details:
        1. Verify conversation exists
        2. Verify conversation belongs to current user
        3. Fetch all messages ordered by timestamp
        4. Return conversation details with messages

    Security:
        - Endpoint requires valid JWT authentication
        - Validates conversation ownership before returning data
        - Only returns conversations and messages from user's own conversations
    """
    try:
        logger.info(f"Retrieving conversation {conversation_id} for user {current_user.id}")

        # Verify conversation exists and belongs to user
        conversation = session.get(Conversation, conversation_id)

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != current_user.id:
            logger.warning(
                f"User {current_user.id} attempted to access conversation {conversation_id} "
                f"owned by user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )

        # Fetch all messages for this conversation
        messages_query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.timestamp.asc())
        )
        messages = session.exec(messages_query).all()

        # Format response
        conversation_summary = ConversationSummary(
            id=str(conversation.id),
            started_at=conversation.started_at.isoformat(),
            ended_at=conversation.ended_at.isoformat() if conversation.ended_at else None,
            duration=conversation.duration_seconds,
            main_topic=conversation.main_topic  # Populated by end_conversation
        )

        message_responses = [
            MessageResponse(
                id=str(msg.id),
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                message_metadata=msg.message_metadata
            )
            for msg in messages
        ]

        logger.info(
            f"Retrieved conversation {conversation_id} with {len(messages)} messages "
            f"for user {current_user.id}"
        )

        return ConversationDetailResponse(
            conversation=conversation_summary,
            messages=message_responses
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error retrieving conversation {conversation_id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}"
        ) from e


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

        # Step 4: Spawn bot in background (non-blocking) with conversation_id for message saving
        logger.info(f"Spawning Pipecat bot for conversation {conversation.id}")
        asyncio.create_task(
            run_bot(
                room_data["room_url"],
                room_data["meeting_token"],
                conversation_id=conversation.id,
                user=current_user
            )
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

        # Step 5b: Generate and save conversation summary
        from src.services.conversation_service import generate_conversation_summary, invalidate_conversation_context_cache

        logger.info(f"Generating conversation summary for {conversation_id}")
        summary = await generate_conversation_summary(conversation_id)

        # Populate summary fields
        conversation.main_topic = summary["main_topic"]
        conversation.key_insights = summary["key_insights"]
        conversation.numbers_discussed = summary["numbers_discussed"]

        logger.info(
            f"Conversation summary generated: topic='{summary['main_topic']}', "
            f"numbers='{summary['numbers_discussed']}'"
        )

        session.commit()
        session.refresh(conversation)

        # Invalidate cached conversation context for this user
        await invalidate_conversation_context_cache(current_user.id)
        logger.info(f"Invalidated conversation context cache for user {current_user.id}")

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


@router.get("/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    conversation_id: UUID,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ConversationMessagesResponse:
    """
    Get messages for a conversation with pagination.

    Retrieves all messages (user and assistant) for a specific conversation,
    ordered by timestamp (oldest first). Supports pagination for conversations
    with many messages.

    Args:
        conversation_id: UUID of the conversation
        page: Page number (1-indexed, default: 1)
        limit: Number of messages per page (default: 50, max: 100)
        current_user: Authenticated user (from JWT token)
        session: Database session

    Returns:
        ConversationMessagesResponse: Paginated messages with metadata:
            {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "messages": [
                    {
                        "id": "...",
                        "role": "user",
                        "content": "What's my life path number?",
                        "timestamp": "2025-11-23T14:00:00Z",
                        "message_metadata": {}
                    },
                    ...
                ],
                "total": 45,
                "page": 1,
                "limit": 50,
                "has_more": false
            }

    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 403: If conversation does not belong to user
        HTTPException 404: If conversation not found
        HTTPException 422: If page or limit parameters are invalid

    Implementation Details:
        1. Validate conversation exists and belongs to current user
        2. Query messages with pagination (LIMIT/OFFSET)
        3. Count total messages for pagination metadata
        4. Return messages ordered by timestamp ascending
        5. Calculate has_more flag based on total and current page

    Security:
        - Endpoint requires valid JWT authentication
        - Validates conversation ownership before returning messages
        - Only returns messages from user's own conversations

    Performance:
        - Uses database indexes on (conversation_id, timestamp)
        - Efficient LIMIT/OFFSET pagination
        - Recommended limit: 50 (default), max: 100
    """
    try:
        # Validate parameters
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page must be >= 1"
            )
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Limit must be between 1 and 100"
            )

        # Step 1: Verify conversation exists and belongs to user
        logger.info(f"Retrieving messages for conversation {conversation_id}, page {page}")
        conversation = session.get(Conversation, conversation_id)

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != current_user.id:
            logger.warning(
                f"User {current_user.id} attempted to access messages for conversation {conversation_id} "
                f"owned by user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )

        # Step 2: Count total messages (using database aggregation for performance)
        total_count_stmt = (
            select(func.count())
            .select_from(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
        )
        total = session.exec(total_count_stmt).one()

        # Step 3: Query messages with pagination
        offset = (page - 1) * limit
        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.timestamp)
            .offset(offset)
            .limit(limit)
        )
        messages = session.exec(query).all()

        # Step 4: Format response
        message_responses = [
            MessageResponse(
                id=str(msg.id),
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                message_metadata=msg.message_metadata
            )
            for msg in messages
        ]

        has_more = (offset + len(messages)) < total

        logger.info(
            f"Retrieved {len(messages)} messages for conversation {conversation_id}, "
            f"page {page} (total: {total})"
        )

        return ConversationMessagesResponse(
            conversation_id=str(conversation_id),
            messages=message_responses,
            total=total,
            page=page,
            limit=limit,
            has_more=has_more
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(
            f"Unexpected error retrieving messages for conversation {conversation_id}: "
            f"{type(e).__name__}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve messages: {str(e)}"
        ) from e
