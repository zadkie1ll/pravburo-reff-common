"""Add partner levels (Старт/Актив/Про/Эксперт): partner_level_months tracks
each agent's level per calendar month, reward_stage_rates gains a `level`
column so the `main` payout amount depends on it, and rewards.application_id
becomes nullable for the quarterly bonus (not tied to a single deal).

Revision ID: 0018
Revises: 0017
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0018"
down_revision: str | Sequence[str] | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"
LEVELS = ["start", "active", "pro", "expert"]


def upgrade() -> None:
    op.create_table(
        "partner_level_months",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("contracts_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.String(10), nullable=False, server_default="start"),
        sa.Column("is_manual", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"]),
        sa.UniqueConstraint(
            "agent_id", "year", "month", name="uq_partner_level_months_agent_period"
        ),
        sa.CheckConstraint("month BETWEEN 1 AND 12", name="ck_partner_level_months_month"),
        sa.CheckConstraint(
            "contracts_count >= 0", name="ck_partner_level_months_contracts_non_negative"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_partner_level_months_agent_id", "partner_level_months", ["agent_id"], schema=SCHEMA
    )

    op.drop_constraint("reward_stage_rates_pkey", "reward_stage_rates", schema=SCHEMA)
    op.add_column(
        "reward_stage_rates",
        sa.Column("level", sa.String(10), nullable=False, server_default="start"),
        schema=SCHEMA,
    )
    op.create_primary_key(
        "reward_stage_rates_pkey", "reward_stage_rates", ["reward_type", "level"], schema=SCHEMA
    )

    rate_rows = sa.table(
        "reward_stage_rates",
        sa.column("reward_type", sa.String(30)),
        sa.column("level", sa.String(10)),
        sa.column("amount", sa.Numeric(12, 2)),
        schema=SCHEMA,
    )
    op.bulk_insert(
        rate_rows,
        [{"reward_type": "advance", "level": level, "amount": 3000} for level in LEVELS[1:]],
    )
    main_amounts = {"start": 13000, "active": 15000, "pro": 18000, "expert": 20000}
    op.execute(
        f"UPDATE {SCHEMA}.reward_stage_rates SET amount = {main_amounts['start']} "
        "WHERE reward_type = 'main' AND level = 'start'"
    )
    op.bulk_insert(
        rate_rows,
        [
            {"reward_type": "main", "level": level, "amount": main_amounts[level]}
            for level in LEVELS[1:]
        ],
    )

    op.alter_column(
        "rewards", "application_id", nullable=True, schema=SCHEMA
    )
    op.create_check_constraint(
        "ck_rewards_quarterly_bonus_no_application",
        "rewards",
        "(reward_type = 'quarterly_bonus' AND application_id IS NULL) "
        "OR (reward_type != 'quarterly_bonus' AND application_id IS NOT NULL)",
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_rewards_quarterly_bonus_no_application", "rewards", schema=SCHEMA, type_="check"
    )
    op.alter_column("rewards", "application_id", nullable=False, schema=SCHEMA)

    op.execute(f"DELETE FROM {SCHEMA}.reward_stage_rates WHERE level != 'start'")
    op.execute(
        f"UPDATE {SCHEMA}.reward_stage_rates SET amount = 10000 "
        "WHERE reward_type = 'main' AND level = 'start'"
    )
    op.drop_constraint("reward_stage_rates_pkey", "reward_stage_rates", schema=SCHEMA)
    op.drop_column("reward_stage_rates", "level", schema=SCHEMA)
    op.create_primary_key(
        "reward_stage_rates_pkey", "reward_stage_rates", ["reward_type"], schema=SCHEMA
    )

    op.drop_table("partner_level_months", schema=SCHEMA)
