"""Track manually imported existing Bitrix clients without creating referral leads.

Revision ID: 0020
Revises: 0019
"""

import sqlalchemy as sa

from alembic import op

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "existing_client_imports",
        sa.Column(
            "application_id",
            sa.BigInteger(),
            sa.ForeignKey("referral.referral_applications.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("deal_id", sa.String(64), nullable=False, unique=True),
        sa.Column("excluded_reward_types", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column(
            "current_reward_id",
            sa.BigInteger(),
            sa.ForeignKey("referral.rewards.id"),
            nullable=True,
        ),
        sa.Column(
            "imported_by_agent_id",
            sa.BigInteger(),
            sa.ForeignKey("referral.agents.id"),
            nullable=False,
        ),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        schema="referral",
    )


def downgrade():
    op.drop_table("existing_client_imports", schema="referral")
