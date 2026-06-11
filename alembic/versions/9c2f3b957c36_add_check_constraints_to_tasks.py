"""add_check_constraints_to_tasks

Revision ID: 9c2f3b957c36
Revises: d875f8c5cd8e
Create Date: 2026-06-10 11:31:25.688106

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9c2f3b957c36'
down_revision: Union[str, Sequence[str], None] = 'd875f8c5cd8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_check_constraint(
        "ck_tasks_priority_range",
        "tasks",
        "priority BETWEEN 1 AND 5"
    )

    op.create_check_constraint(
        "ck_tasks_title_length",
        "tasks",
        "length(title) BETWEEN 1 AND 200"
    )

    op.create_check_constraint(
        "ck_tasks_soft_delete_consistency",
        "tasks",
        "( (is_deleted = false AND deleted_at IS NULL) OR (is_deleted = true AND deleted_at IS NOT NULL) )"
    )


def downgrade():
    op.drop_constraint("ck_tasks_soft_delete_consistency", "tasks", type_="check")
    op.drop_constraint("ck_tasks_title_length", "tasks", type_="check")
    op.drop_constraint("ck_tasks_priority_range", "tasks", type_="check")
