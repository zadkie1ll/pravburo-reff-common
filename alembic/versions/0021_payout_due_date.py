"""Allow an explicit payout deadline without changing approval history.

Revision ID: 0021
Revises: 0020
"""

import sqlalchemy as sa

from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "rewards", sa.Column("payout_due_date", sa.Date(), nullable=True), schema="referral"
    )


def downgrade():
    op.drop_column("rewards", "payout_due_date", schema="referral")
