"""Add bitrix_deal_id and deal_stage_code to referral_applications, for
reverse sync from Bitrix (deal stage -> partner-facing client status,
ТЗ п.4 + п.10). Populated by pravburo-reff-crm's deal webhook.

Revision ID: 0015
Revises: 0014
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0015"
down_revision: str | Sequence[str] | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "referral_applications",
        sa.Column("bitrix_deal_id", sa.String(64), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "referral_applications",
        sa.Column("deal_stage_code", sa.String(64), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("referral_applications", "deal_stage_code", schema=SCHEMA)
    op.drop_column("referral_applications", "bitrix_deal_id", schema=SCHEMA)
