"""Remove foreign key from essay_evaluations.essay_id

Revision ID: a47489ac3ad5
Revises: 0c42eb7d2c1f
Create Date: 2025-06-08 15:44:32.142061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a47489ac3ad5'
down_revision: Union[str, None] = '0c42eb7d2c1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop FK from essay_evaluations.essay_id
    op.drop_constraint('essay_evaluations_essay_id_fkey', 'essay_evaluations', type_='foreignkey')

    # Drop FK from essay_summaries.essay_id
    op.drop_constraint('essay_summaries_essay_id_fkey', 'essay_summaries', type_='foreignkey')


def downgrade():
    # Recreate FK for essay_evaluations.essay_id
    op.create_foreign_key(
        'essay_evaluations_essay_id_fkey',
        'essay_evaluations', 'essay',
        ['essay_id'], ['id']
    )

    # Recreate FK for essay_summaries.essay_id
    op.create_foreign_key(
        'essay_summaries_essay_id_fkey',
        'essay_summaries', 'essay',
        ['essay_id'], ['id']
    )