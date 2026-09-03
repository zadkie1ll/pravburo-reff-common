"""Add partner-invites-partner network: invited_by link, and override rewards.

A partner can invite up to 2 levels of override on downline reward events
(3 people share one payout: the earner, plus 2 levels above). A legacy-client
earner (Agent.legacy_client_id is set - i.e. someone who came to Pravburo as
a bankruptcy client, not someone who consciously registered as a partner)
caps override one level shorter than a partner earner - that's calculated in
application code from Agent.legacy_client_id, not stored separately here.

Override rewards reuse the existing `rewards` table (reward_type='override'),
tied back to the reward that triggered them via source_reward_id. A deal can
carry several source rewards (advance, main, bonus...), each generating its
own override to the same upline agent, so the old single unique constraint on
deal_id can't be reused as-is for overrides - split into two partial unique
indexes instead, one per reward "shape" (plain vs. override).

Revision ID: 0007
Revises: 0006
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | Sequence[str] | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("invited_by_agent_id", sa.BigInteger(), nullable=True),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_agents_invited_by_agent_id",
        "agents",
        "agents",
        ["invited_by_agent_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
    )
    op.create_index(
        "ix_agents_invited_by_agent_id", "agents", ["invited_by_agent_id"], schema=SCHEMA
    )

    op.create_table(
        "network_override_rates",
        sa.Column("level", sa.Integer(), primary_key=True),
        sa.Column("percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("level IN (1, 2)", name="ck_network_override_rates_level"),
        sa.CheckConstraint(
            "percent >= 0", name="ck_network_override_rates_percent_non_negative"
        ),
        schema=SCHEMA,
    )
    op.bulk_insert(
        sa.table(
            "network_override_rates",
            sa.column("level", sa.Integer()),
            sa.column("percent", sa.Numeric(5, 2)),
            schema=SCHEMA,
        ),
        [
            {"level": 1, "percent": 10},
            {"level": 2, "percent": 5},
        ],
    )

    op.drop_constraint("ck_rewards_reward_type", "rewards", schema=SCHEMA, type_="check")
    op.create_check_constraint(
        "ck_rewards_reward_type",
        "rewards",
        "reward_type IN ('advance', 'main', 'bonus_full_payment', 'quarterly_bonus', 'override')",
        schema=SCHEMA,
    )
    op.add_column(
        "rewards",
        sa.Column("network_level", sa.Integer(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "rewards",
        sa.Column("source_reward_id", sa.BigInteger(), nullable=True),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_rewards_source_reward_id",
        "rewards",
        "rewards",
        ["source_reward_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
    )

    op.drop_constraint("uq_rewards_deal_id", "rewards", schema=SCHEMA, type_="unique")
    op.create_index(
        "uq_rewards_deal_id_reward_type_agent_id",
        "rewards",
        ["deal_id", "reward_type", "agent_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where="source_reward_id IS NULL",
    )
    op.create_index(
        "uq_rewards_source_reward_id_agent_id",
        "rewards",
        ["source_reward_id", "agent_id"],
        unique=True,
        schema=SCHEMA,
        postgresql_where="source_reward_id IS NOT NULL",
    )
    op.create_check_constraint(
        "ck_rewards_network_level", "rewards", "network_level IN (1, 2)", schema=SCHEMA
    )
    op.create_check_constraint(
        "ck_rewards_override_shape",
        "rewards",
        "(reward_type = 'override' AND source_reward_id IS NOT NULL "
        "AND network_level IS NOT NULL) "
        "OR (reward_type != 'override' AND source_reward_id IS NULL "
        "AND network_level IS NULL)",
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint("ck_rewards_override_shape", "rewards", schema=SCHEMA, type_="check")
    op.drop_constraint("ck_rewards_network_level", "rewards", schema=SCHEMA, type_="check")
    op.drop_index("uq_rewards_source_reward_id_agent_id", table_name="rewards", schema=SCHEMA)
    op.drop_index(
        "uq_rewards_deal_id_reward_type_agent_id", table_name="rewards", schema=SCHEMA
    )
    op.create_unique_constraint("uq_rewards_deal_id", "rewards", ["deal_id"], schema=SCHEMA)

    op.drop_constraint(
        "fk_rewards_source_reward_id", "rewards", schema=SCHEMA, type_="foreignkey"
    )
    op.drop_column("rewards", "source_reward_id", schema=SCHEMA)
    op.drop_column("rewards", "network_level", schema=SCHEMA)

    op.drop_constraint("ck_rewards_reward_type", "rewards", schema=SCHEMA, type_="check")
    op.create_check_constraint(
        "ck_rewards_reward_type",
        "rewards",
        "reward_type IN ('advance', 'main', 'bonus_full_payment', 'quarterly_bonus')",
        schema=SCHEMA,
    )

    op.drop_table("network_override_rates", schema=SCHEMA)

    op.drop_index("ix_agents_invited_by_agent_id", table_name="agents", schema=SCHEMA)
    op.drop_constraint(
        "fk_agents_invited_by_agent_id", "agents", schema=SCHEMA, type_="foreignkey"
    )
    op.drop_column("agents", "invited_by_agent_id", schema=SCHEMA)
