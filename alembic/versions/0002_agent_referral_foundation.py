"""Add agent accounts, referral attribution and reward review.

Revision ID: 0002
Revises: 0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("phone_normalized", sa.String(20), nullable=True),
        sa.Column("display_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("role", sa.String(5), nullable=False, server_default="agent"),
        sa.Column("referral_code", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("legacy_client_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('agent', 'admin')", name="ck_agents_role"),
        sa.UniqueConstraint("email", name="uq_agents_email"),
        sa.UniqueConstraint("phone_normalized", name="uq_agents_phone_normalized"),
        sa.UniqueConstraint("referral_code", name="uq_agents_referral_code"),
        sa.UniqueConstraint("legacy_client_id", name="uq_agents_legacy_client_id"),
        schema=SCHEMA,
    )
    op.create_index("ix_agents_email", "agents", ["email"], schema=SCHEMA)
    op.create_index("ix_agents_phone_normalized", "agents", ["phone_normalized"], schema=SCHEMA)
    op.create_index("ix_agents_referral_code", "agents", ["referral_code"], schema=SCHEMA)
    op.create_table(
        "agent_credentials",
        sa.Column("agent_id", sa.BigInteger(), primary_key=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"], ondelete="CASCADE"),
        schema=SCHEMA,
    )
    op.create_table(
        "agent_identities",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("provider", "subject", name="uq_agent_identity_provider_subject"),
        schema=SCHEMA,
    )
    op.create_index("ix_agent_identities_agent_id", "agent_identities", ["agent_id"], schema=SCHEMA)
    op.create_table(
        "pending_registrations",
        sa.Column("token", sa.String(64), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_pending_registrations_email", "pending_registrations", ["email"], schema=SCHEMA
    )
    op.create_table(
        "pending_password_resets",
        sa.Column("token", sa.String(64), primary_key=True),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("code_hash", sa.String(64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"], ondelete="CASCADE"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_pending_password_resets_email", "pending_password_resets", ["email"], schema=SCHEMA
    )
    op.create_table(
        "referral_applications",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone_normalized", sa.String(20), nullable=False),
        sa.Column("preferred_call_time_msk", sa.String(100), nullable=True),
        sa.Column("city", sa.String(120), nullable=True),
        sa.Column("debt_amount", sa.String(80), nullable=True),
        sa.Column("situation", sa.Text(), nullable=True),
        sa.Column("delivery_status", sa.String(7), nullable=False, server_default="pending"),
        sa.Column("bitrix_lead_id", sa.String(64), nullable=True),
        sa.Column("delivery_error", sa.String(300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "delivery_status IN ('pending', 'sent', 'failed')",
            name="ck_referral_applications_delivery_status",
        ),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"]),
        sa.UniqueConstraint("phone_normalized", name="uq_referral_application_phone"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_referral_applications_agent_id", "referral_applications", ["agent_id"], schema=SCHEMA
    )
    op.create_index(
        "ix_referral_applications_agent_created",
        "referral_applications",
        ["agent_id", "created_at"],
        schema=SCHEMA,
    )
    op.create_table(
        "rewards",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("deal_id", sa.String(64), nullable=False),
        sa.Column("application_id", sa.BigInteger(), nullable=False),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(8), nullable=False, server_default="pending"),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by_agent_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')", name="ck_rewards_status"
        ),
        sa.ForeignKeyConstraint(["application_id"], ["referral.referral_applications.id"]),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"]),
        sa.ForeignKeyConstraint(["decided_by_agent_id"], ["referral.agents.id"]),
        sa.UniqueConstraint("deal_id", name="uq_rewards_deal_id"),
        sa.UniqueConstraint("application_id", name="uq_rewards_application_id"),
        schema=SCHEMA,
    )
    op.create_index("ix_rewards_deal_id", "rewards", ["deal_id"], schema=SCHEMA)
    op.create_index("ix_rewards_agent_id", "rewards", ["agent_id"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_table("rewards", schema=SCHEMA)
    op.drop_table("referral_applications", schema=SCHEMA)
    op.drop_table("pending_password_resets", schema=SCHEMA)
    op.drop_table("pending_registrations", schema=SCHEMA)
    op.drop_table("agent_credentials", schema=SCHEMA)
    op.drop_table("agent_identities", schema=SCHEMA)
    op.drop_table("agents", schema=SCHEMA)
