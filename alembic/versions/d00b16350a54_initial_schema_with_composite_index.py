"""initial_schema_with_composite_index

Revision ID: d00b16350a54
Revises: 
Create Date: 2026-05-27 10:27:47.704868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd00b16350a54'
down_revision: Union[str, Sequence[str], None] = '039920450ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_tasks_user_id_completed_priority",
        "tasks",
        ["user_id", "completed", "priority"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_tasks_user_id_completed_priority",
        table_name="tasks",
    )
