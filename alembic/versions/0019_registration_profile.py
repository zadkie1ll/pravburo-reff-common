"""Store required partner profile data with pending registrations.

Revision ID: 0019
Revises: 0018
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0019"
down_revision: str | Sequence[str] | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "pending_registrations",
        sa.Column("display_name", sa.String(200), nullable=False, server_default=""),
        schema=SCHEMA,
    )
    op.add_column(
        "pending_registrations",
        sa.Column("employment_format", sa.String(30), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "pending_registrations",
        sa.Column("payout_details", sa.String(200), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "pending_registrations",
        sa.Column("inn", sa.String(12), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("pending_registrations", "inn", schema=SCHEMA)
    op.drop_column("pending_registrations", "payout_details", schema=SCHEMA)
    op.drop_column("pending_registrations", "employment_format", schema=SCHEMA)
    op.drop_column("pending_registrations", "display_name", schema=SCHEMA)
