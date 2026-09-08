"""Add due/overdue admin-notice dedup flags to rewards, for the hourly
Telegram scheduler that alerts admins about upcoming and overdue payouts.

Revision ID: 0012
Revises: 0011
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0012"
down_revision: str | Sequence[str] | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "rewards",
        sa.Column("due_notice_sent_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "rewards",
        sa.Column("overdue_notice_sent_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("rewards", "overdue_notice_sent_at", schema=SCHEMA)
    op.drop_column("rewards", "due_notice_sent_at", schema=SCHEMA)
