"""Add reward_type/amount/paid_at to rewards; allow multiple rewards per application.

Revision ID: 0006
Revises: 0005
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | Sequence[str] | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "rewards",
        sa.Column("reward_type", sa.String(24), nullable=False, server_default="main"),
        schema=SCHEMA,
    )
    op.add_column(
        "rewards",
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "rewards",
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_rewards_reward_type",
        "rewards",
        "reward_type IN ('advance', 'main', 'bonus_full_payment', 'quarterly_bonus')",
        schema=SCHEMA,
    )
    op.drop_constraint("uq_rewards_application_id", "rewards", schema=SCHEMA, type_="unique")
    op.create_index("ix_rewards_application_id", "rewards", ["application_id"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_rewards_application_id", table_name="rewards", schema=SCHEMA)
    op.create_unique_constraint(
        "uq_rewards_application_id", "rewards", ["application_id"], schema=SCHEMA
    )
    op.drop_constraint("ck_rewards_reward_type", "rewards", schema=SCHEMA, type_="check")
    op.drop_column("rewards", "paid_at", schema=SCHEMA)
    op.drop_column("rewards", "amount", schema=SCHEMA)
    op.drop_column("rewards", "reward_type", schema=SCHEMA)
