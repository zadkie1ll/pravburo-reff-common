"""Add partner profile fields to agents: employment format, payout details, INN, active status.

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("employment_format", sa.String(24), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "agents",
        sa.Column("payout_details", sa.String(200), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "agents",
        sa.Column("inn", sa.String(12), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "agents",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_agents_employment_format",
        "agents",
        "employment_format IN ('self_employed', 'individual_entrepreneur', 'individual')",
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint("ck_agents_employment_format", "agents", schema=SCHEMA, type_="check")
    op.drop_column("agents", "is_active", schema=SCHEMA)
    op.drop_column("agents", "inn", schema=SCHEMA)
    op.drop_column("agents", "payout_details", schema=SCHEMA)
    op.drop_column("agents", "employment_format", schema=SCHEMA)
