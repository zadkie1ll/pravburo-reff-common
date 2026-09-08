"""Add processing_status and assigned_manager_id to referral_applications,
for the admin "Заявки" panel's manager assignment and workflow tracking
(separate from delivery_status, which only tracks Bitrix CRM delivery).

Revision ID: 0013
Revises: 0012
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0013"
down_revision: str | Sequence[str] | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.add_column(
        "referral_applications",
        sa.Column(
            "processing_status", sa.String(11), nullable=False, server_default="new"
        ),
        schema=SCHEMA,
    )
    op.create_check_constraint(
        "ck_referral_applications_processing_status",
        "referral_applications",
        "processing_status IN ('new', 'in_progress', 'closed')",
        schema=SCHEMA,
    )
    op.add_column(
        "referral_applications",
        sa.Column("assigned_manager_id", sa.BigInteger(), nullable=True),
        schema=SCHEMA,
    )
    op.create_foreign_key(
        "fk_referral_applications_assigned_manager_id",
        "referral_applications",
        "agents",
        ["assigned_manager_id"],
        ["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_referral_applications_assigned_manager_id",
        "referral_applications",
        schema=SCHEMA,
        type_="foreignkey",
    )
    op.drop_column("referral_applications", "assigned_manager_id", schema=SCHEMA)
    op.drop_constraint(
        "ck_referral_applications_processing_status",
        "referral_applications",
        schema=SCHEMA,
        type_="check",
    )
    op.drop_column("referral_applications", "processing_status", schema=SCHEMA)
