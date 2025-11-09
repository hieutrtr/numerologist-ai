"""
Conversation Model

Defines the Conversation database model for managing voice conversation sessions.
This model tracks the lifecycle of voice conversations between users and the AI bot,
including room management, timing, and duration calculation.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional


class Conversation(SQLModel, table=True):
    """
    Conversation model for voice interaction sessions.

    Tracks voice conversation lifecycle including Daily.co room management,
    timing information, and bot interaction state. Each conversation represents
    a single session between a user and the AI numerologist bot.

    Fields:
    - id: Unique conversation identifier (UUID)
    - user_id: Foreign key to User (conversation owner)
    - daily_room_id: Daily.co room identifier/name for WebRTC connection
    - started_at: Timestamp when conversation began
    - ended_at: Timestamp when conversation ended (NULL if ongoing)
    - duration_seconds: Total duration in seconds (calculated from ended_at - started_at)
    - created_at: Audit timestamp (when record was created)
    - updated_at: Audit timestamp (last modification time)

    Relationships:
    - user: Many-to-one relationship with User (owner of conversation)

    Usage:
    ```python
    # Create conversation
    conversation = Conversation(user_id=user.id)
    session.add(conversation)
    session.commit()

    # Query user's conversations
    user_conversations = user.conversations  # Access via relationship

    # Calculate duration when ending
    conversation.ended_at = datetime.now(timezone.utc)
    conversation.calculate_duration()
    session.commit()
    ```
    """

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the conversation"
    )

    # Foreign key to User
    user_id: UUID = Field(
        foreign_key="user.id",
        description="User who owns this conversation (required)"
    )

    # Room management
    daily_room_id: Optional[str] = Field(
        default=None,
        description="Daily.co room identifier/name for WebRTC connection"
    )

    # Timing fields
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when conversation started"
    )
    ended_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when conversation ended (NULL if still active)"
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        description="Total conversation duration in seconds (calculated when ended_at is set)"
    )

    # Audit fields
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when record was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of last modification"
    )

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="conversations",
    )

    def calculate_duration(self) -> None:
        """
        Calculate and update the duration_seconds field.

        Should be called after setting ended_at to compute the total conversation duration.
        If ended_at is not set or is before started_at, duration remains unchanged.

        Example:
        ```python
        conversation.ended_at = datetime.now(timezone.utc)
        conversation.calculate_duration()
        # Now conversation.duration_seconds is updated
        ```
        """
        if self.ended_at and self.started_at:
            delta = self.ended_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
