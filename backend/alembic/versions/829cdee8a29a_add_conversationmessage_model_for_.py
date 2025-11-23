"""Add ConversationMessage model for message history

Revision ID: 829cdee8a29a
Revises: 5f0f00efe0dd
Create Date: 2025-11-23 14:27:01.578093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '829cdee8a29a'
down_revision: Union[str, Sequence[str], None] = '5f0f00efe0dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create message_role enum type
    op.execute("CREATE TYPE message_role AS ENUM ('user', 'assistant')")

    # Create conversation_message table
    op.create_table(
        'conversation_message',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='message_role', native_enum=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('message_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], name='fk_conversation_message_conversation_id'),
        sa.PrimaryKeyConstraint('id', name='pk_conversation_message')
    )

    # Create indexes for fast queries
    op.create_index('ix_conversation_message_conversation_id', 'conversation_message', ['conversation_id'])
    op.create_index('ix_conversation_message_timestamp', 'conversation_message', ['timestamp'])
    # Composite index for ordered message retrieval
    op.create_index('ix_conversation_message_conv_timestamp', 'conversation_message', ['conversation_id', 'timestamp'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_conversation_message_conv_timestamp', table_name='conversation_message')
    op.drop_index('ix_conversation_message_timestamp', table_name='conversation_message')
    op.drop_index('ix_conversation_message_conversation_id', table_name='conversation_message')

    # Drop table
    op.drop_table('conversation_message')

    # Drop enum type
    op.execute("DROP TYPE message_role")
