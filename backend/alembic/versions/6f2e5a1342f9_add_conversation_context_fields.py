"""add_conversation_context_fields

Revision ID: 6f2e5a1342f9
Revises: 829cdee8a29a
Create Date: 2025-11-23 20:44:53.015492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f2e5a1342f9'
down_revision: Union[str, Sequence[str], None] = '829cdee8a29a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add conversation context fields for AI context retrieval."""
    # Add main_topic column
    op.add_column('conversation', sa.Column('main_topic', sa.String(), nullable=True))

    # Add key_insights column
    op.add_column('conversation', sa.Column('key_insights', sa.String(), nullable=True))

    # Add numbers_discussed column (stores JSON array as string)
    op.add_column('conversation', sa.Column('numbers_discussed', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove conversation context fields."""
    # Drop columns in reverse order
    op.drop_column('conversation', 'numbers_discussed')
    op.drop_column('conversation', 'key_insights')
    op.drop_column('conversation', 'main_topic')
