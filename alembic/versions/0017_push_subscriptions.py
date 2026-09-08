"""Add push_subscriptions for browser Web Push notifications to partners
(ТЗ п.6 "Push в браузере").

Revision ID: 0017
Revises: 0016
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0017"
down_revision: str | Sequence[str] | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("agent_id", sa.BigInteger(), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("p256dh", sa.String(200), nullable=False),
        sa.Column("auth", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["agent_id"], ["referral.agents.id"]),
        sa.UniqueConstraint("endpoint", name="uq_push_subscriptions_endpoint"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_push_subscriptions_agent_id", "push_subscriptions", ["agent_id"], schema=SCHEMA
    )


def downgrade() -> None:
    op.drop_table("push_subscriptions", schema=SCHEMA)
