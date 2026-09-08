"""Add reward_stage_rates: admin-editable flat amounts for the advance
(contract signed) and main (deposit paid) payouts, driven by real Bitrix
deal stage transitions in pravburo-reff-crm.

Revision ID: 0016
Revises: 0015
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0016"
down_revision: str | Sequence[str] | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.create_table(
        "reward_stage_rates",
        sa.Column("reward_type", sa.String(30), primary_key=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "reward_type IN ('advance', 'main')", name="ck_reward_stage_rates_type"
        ),
        sa.CheckConstraint("amount >= 0", name="ck_reward_stage_rates_amount_non_negative"),
        schema=SCHEMA,
    )
    op.bulk_insert(
        sa.table(
            "reward_stage_rates",
            sa.column("reward_type", sa.String(30)),
            sa.column("amount", sa.Numeric(12, 2)),
            schema=SCHEMA,
        ),
        [
            {"reward_type": "advance", "amount": 3000},
            {"reward_type": "main", "amount": 10000},
        ],
    )


def downgrade() -> None:
    op.drop_table("reward_stage_rates", schema=SCHEMA)
