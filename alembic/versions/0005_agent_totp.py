"""Add TOTP two-factor auth fields to agents (used for admin login).

Revision ID: 0005
Revises: 0004
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | Sequence[str] | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("totp_secret", sa.String(32), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "agents",
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default="false"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("agents", "totp_enabled", schema=SCHEMA)
    op.drop_column("agents", "totp_secret", schema=SCHEMA)
