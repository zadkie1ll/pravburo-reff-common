"""Add payout_settings singleton table for the admin "Выплаты" panel's
configurable overdue threshold.

Revision ID: 0010
Revises: 0009
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010"
down_revision: str | Sequence[str] | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.create_table(
        "payout_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("overdue_days", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("overdue_days > 0", name="ck_payout_settings_overdue_days_positive"),
        schema=SCHEMA,
    )
    op.bulk_insert(
        sa.table(
            "payout_settings",
            sa.column("id", sa.Integer()),
            sa.column("overdue_days", sa.Integer()),
            schema=SCHEMA,
        ),
        [{"id": 1, "overdue_days": 14}],
    )


def downgrade() -> None:
    op.drop_table("payout_settings", schema=SCHEMA)
