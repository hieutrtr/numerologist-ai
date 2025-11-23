"""
Conversation Message Model

Defines the ConversationMessage database model for storing individual messages
within voice conversation sessions. This model captures both user and assistant
messages with their content, timestamps, and optional metadata.
"""

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, JSON, Enum as SQLEnum
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum


class MessageRole(str, Enum):
    """Enum for message role types."""
    USER = "user"
    ASSISTANT = "assistant"


class ConversationMessage(SQLModel, table=True):
    """
    ConversationMessage model for storing individual messages in conversations.

    Tracks each message exchanged during a voice conversation between the user
    and the AI bot. Messages are stored with their role (user/assistant), content,
    timestamp, and optional metadata for future analysis.

    Fields:
    - id: Unique message identifier (UUID)
    - conversation_id: Foreign key to Conversation (parent conversation)
    - role: Message sender (user or assistant)
    - content: Full text content of the message
    - timestamp: When the message was created
    - message_metadata: Optional JSON field for additional data (sentiment, confidence, etc.)

    Relationships:
    - conversation: Many-to-one relationship with Conversation

    Indexes:
    - conversation_id: For fast retrieval of all messages in a conversation
    - (conversation_id, timestamp): For ordered message queries

    Usage:
    ```python
    # Save user message
    user_msg = ConversationMessage(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="What's my life path number?"
    )
    session.add(user_msg)

    # Save assistant message with metadata
    ai_msg = ConversationMessage(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="Based on your birth date...",
        message_metadata={"function_calls": ["calculate_life_path"]}
    )
    session.add(ai_msg)
    session.commit()

    # Query messages for conversation
    messages = session.exec(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conv.id)
        .order_by(ConversationMessage.timestamp)
    ).all()
    ```
    """

    __tablename__ = "conversation_message"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the message"
    )

    # Foreign key to Conversation
    conversation_id: UUID = Field(
        foreign_key="conversation.id",
        index=True,
        description="Conversation this message belongs to (required)"
    )

    # Message fields
    role: MessageRole = Field(
        sa_column=Column(
            SQLEnum(MessageRole, name="message_role", native_enum=False),
            nullable=False
        ),
        description="Role of the message sender (user or assistant)"
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Full text content of the message"
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
        description="Timestamp when message was created"
    )

    message_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Optional metadata (function calls, sentiment, confidence, etc.)"
    )

    # Relationships
    conversation: Optional["Conversation"] = Relationship(
        back_populates="messages"
    )
