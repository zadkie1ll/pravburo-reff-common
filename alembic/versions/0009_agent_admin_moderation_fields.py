"""Add blocked_reason and admin_note to Agent for the admin "Партнёры" panel.

Revision ID: 0009
Revises: 0008
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009"
down_revision: str | Sequence[str] | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("blocked_reason", sa.Text(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "agents",
        sa.Column("admin_note", sa.Text(), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("agents", "admin_note", schema=SCHEMA)
    op.drop_column("agents", "blocked_reason", schema=SCHEMA)
