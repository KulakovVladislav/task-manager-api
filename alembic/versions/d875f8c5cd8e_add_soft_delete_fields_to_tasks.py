"""add_soft_delete_fields_to_tasks

Revision ID: d875f8c5cd8e
Revises: ba3862f1e6fc
Create Date: 2026-06-06 18:10:59.597745

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd875f8c5cd8e'
down_revision: Union[str, Sequence[str], None] = 'ba3862f1e6fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'tasks',
        sa.Column('is_deleted', sa.Boolean(),
                  server_default=sa.text('false'), nullable=False)
    )
    op.add_column(
        'tasks',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tasks', 'deleted_at')
    op.drop_column('tasks', 'is_deleted')
    pass
