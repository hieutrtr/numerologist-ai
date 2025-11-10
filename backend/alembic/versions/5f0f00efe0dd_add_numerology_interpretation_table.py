"""add_numerology_interpretation_table

Revision ID: 5f0f00efe0dd
Revises: 7a8b9c0d1e2f
Create Date: 2025-11-10 16:56:26.675792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f0f00efe0dd'
down_revision: Union[str, Sequence[str], None] = '7a8b9c0d1e2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create numerology_interpretation table."""
    # Create numerology_interpretation table
    op.create_table(
        'numerology_interpretation',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('number_type', sa.String(), nullable=False),
        sa.Column('number_value', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for query performance
    op.create_index(
        'ix_numerology_interpretation_number_type',
        'numerology_interpretation',
        ['number_type'],
        unique=False
    )
    op.create_index(
        'ix_numerology_interpretation_number_value',
        'numerology_interpretation',
        ['number_value'],
        unique=False
    )
    # Composite index for common query pattern (number_type + number_value)
    op.create_index(
        'ix_numerology_interpretation_type_value',
        'numerology_interpretation',
        ['number_type', 'number_value'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema - drop numerology_interpretation table."""
    # Drop indexes first
    op.drop_index('ix_numerology_interpretation_type_value', table_name='numerology_interpretation')
    op.drop_index('ix_numerology_interpretation_number_value', table_name='numerology_interpretation')
    op.drop_index('ix_numerology_interpretation_number_type', table_name='numerology_interpretation')
    # Drop table
    op.drop_table('numerology_interpretation')
