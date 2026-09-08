"""Drop the permanent UNIQUE on referral_applications.phone_normalized so a
client-agent fixation can expire after 180 days without a reward (ТЗ п.12).
Replaced with a plain (phone, created_at) index for the expiry lookup.

Revision ID: 0014
Revises: 0013
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0014"
down_revision: str | Sequence[str] | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"


def upgrade() -> None:
    op.drop_constraint(
        "uq_referral_application_phone",
        "referral_applications",
        schema=SCHEMA,
        type_="unique",
    )
    op.create_index(
        "ix_referral_applications_phone_created",
        "referral_applications",
        ["phone_normalized", "created_at"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_referral_applications_phone_created",
        table_name="referral_applications",
        schema=SCHEMA,
    )
    op.create_unique_constraint(
        "uq_referral_application_phone",
        "referral_applications",
        ["phone_normalized"],
        schema=SCHEMA,
    )
