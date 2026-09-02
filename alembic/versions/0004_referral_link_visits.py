"""Add referral_link_visits to track visits to an agent's application link.

Revision ID: 0004
Revises: 0003
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.create_table(
        "referral_link_visits",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"]),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_referral_link_visits_agent_id", "referral_link_visits", ["agent_id"], schema=SCHEMA
    )
    op.create_index(
        "ix_referral_link_visits_agent_created",
        "referral_link_visits",
        ["agent_id", "created_at"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("referral_link_visits", schema=SCHEMA)
