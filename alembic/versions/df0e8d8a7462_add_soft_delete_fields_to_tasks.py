from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "df0e8d8a7462"
down_revision: Union[str, Sequence[str], None] = "d00b16350a54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "tasks",
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.alter_column(
        "tasks",
        "is_deleted",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("tasks", "deleted_at")
    op.drop_column("tasks", "is_deleted")
