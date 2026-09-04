"""Switch NetworkOverrideRate to a flat sum per level, and widen it to 3 levels.

Product decided override payouts shouldn't scale with the downline's own
reward amount - each level pays a fixed sum instead, regardless of what the
earner made. Existing percent values don't translate to a sum, so this
resets levels to sensible flat defaults; an admin can retune them at
/admin/network/rates right after deploy.

Also widens the override depth from 2 to 3 levels: a partner-type earner
(self-registered) now pays override 3 levels up instead of 2; a client-type
earner (auto-created, never registered) pays 2 levels up instead of 1. See
bounty's _max_override_levels for the actual level-count-by-earner-type split
- this migration only adds the level-3 row and widens the constraints that
capped it at 2.

Revision ID: 0008
Revises: 0007
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | Sequence[str] | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.drop_constraint(
        "ck_network_override_rates_percent_non_negative",
        "network_override_rates",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_constraint(
        "ck_network_override_rates_level", "network_override_rates", schema=SCHEMA, type_="check"
    )
    op.add_column(
        "network_override_rates",
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        schema=SCHEMA,
    )
    op.execute("UPDATE referral.network_override_rates SET amount = 500 WHERE level = 1")
    op.execute("UPDATE referral.network_override_rates SET amount = 200 WHERE level = 2")
    op.alter_column("network_override_rates", "amount", nullable=False, schema=SCHEMA)
    op.drop_column("network_override_rates", "percent", schema=SCHEMA)
    op.create_check_constraint(
        "ck_network_override_rates_amount_non_negative",
        "network_override_rates",
        "amount >= 0",
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_network_override_rates_level",
        "network_override_rates",
        "level IN (1, 2, 3)",
        schema=SCHEMA,
    )
    op.execute(
        "INSERT INTO referral.network_override_rates (level, amount) VALUES (3, 100)"
    )

    op.drop_constraint("ck_rewards_network_level", "rewards", schema=SCHEMA, type_="check")
    op.create_check_constraint(
        "ck_rewards_network_level", "rewards", "network_level IN (1, 2, 3)", schema=SCHEMA
    )


def downgrade() -> None:
    op.drop_constraint("ck_rewards_network_level", "rewards", schema=SCHEMA, type_="check")
    op.execute("DELETE FROM referral.rewards WHERE network_level = 3")
    op.create_check_constraint(
        "ck_rewards_network_level", "rewards", "network_level IN (1, 2)", schema=SCHEMA
    )

    op.execute("DELETE FROM referral.network_override_rates WHERE level = 3")
    op.drop_constraint(
        "ck_network_override_rates_level", "network_override_rates", schema=SCHEMA, type_="check"
    )
    op.drop_constraint(
        "ck_network_override_rates_amount_non_negative",
        "network_override_rates",
        schema=SCHEMA,
        type_="check",
    )
    op.add_column(
        "network_override_rates",
        sa.Column("percent", sa.Numeric(5, 2), nullable=True),
        schema=SCHEMA,
    )
    op.execute("UPDATE referral.network_override_rates SET percent = 10 WHERE level = 1")
    op.execute("UPDATE referral.network_override_rates SET percent = 5 WHERE level = 2")
    op.alter_column("network_override_rates", "percent", nullable=False, schema=SCHEMA)
    op.drop_column("network_override_rates", "amount", schema=SCHEMA)
    op.create_check_constraint(
        "ck_network_override_rates_percent_non_negative",
        "network_override_rates",
        "percent >= 0",
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_network_override_rates_level",
        "network_override_rates",
        "level IN (1, 2)",
        schema=SCHEMA,
    )
