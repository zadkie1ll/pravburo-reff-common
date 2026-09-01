"""Create the namespace in the dedicated Referral PostgreSQL.

Revision ID: 0001
Revises:
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS referral")


def downgrade() -> None:
    # Intentionally keep the namespace: a future schema may contain business data.
    pass
