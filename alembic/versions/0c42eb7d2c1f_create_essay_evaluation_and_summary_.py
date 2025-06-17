"""Create essay evaluation and summary tables

Revision ID: 0c42eb7d2c1f
Revises: 
Create Date: 2025-06-08 14:51:10.387698
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision: str = '0c42eb7d2c1f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema by adding new tables."""
    op.create_table(
        'essay_evaluations',
        sa.Column('id', sa.String(), primary_key=True, default=lambda: str(uuid.uuid4()), index=True),
        sa.Column('essay_id', sa.Integer(), sa.ForeignKey('essay.id'), nullable=False),
        sa.Column('criterion', sa.String(), nullable=True),
        sa.Column('matched_label', sa.String(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('max_score', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('suggestion', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False)
    )

    op.create_table(
        'essay_summaries',
        sa.Column('id', sa.String(), primary_key=True, default=lambda: str(uuid.uuid4()), index=True),
        sa.Column('essay_id', sa.Integer(), sa.ForeignKey('essay.id'), nullable=False),
        sa.Column('total_score', sa.Integer(), nullable=True),
        sa.Column('max_total_score', sa.Integer(), nullable=True),
        sa.Column('overall_feedback', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema by removing new tables."""
    op.drop_table('essay_summaries')
    op.drop_table('essay_evaluations')
