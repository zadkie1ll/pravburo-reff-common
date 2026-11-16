"""Store the manual settlement workflow of existing clients.

Revision ID: 0022
Revises: 0021
"""

import sqlalchemy as sa

from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("ck_rewards_reward_type", "rewards", schema="referral", type_="check")
    op.create_check_constraint(
        "ck_rewards_reward_type",
        "rewards",
        "reward_type IN ('advance', 'main', 'bonus_full_payment', "
        "'quarterly_bonus', 'override', 'curator')",
        schema="referral",
    )
    op.add_column(
        "existing_client_imports",
        sa.Column("workflow_data", sa.JSON(), nullable=True),
        schema="referral",
    )


def downgrade():
    # PostgreSQL refuses the downgrade while curator rewards exist; never drop financial rows.
    op.drop_constraint("ck_rewards_reward_type", "rewards", schema="referral", type_="check")
    op.create_check_constraint(
        "ck_rewards_reward_type",
        "rewards",
        "reward_type IN ('advance', 'main', 'bonus_full_payment', 'quarterly_bonus', 'override')",
        schema="referral",
    )
    op.drop_column("existing_client_imports", "workflow_data", schema="referral")
