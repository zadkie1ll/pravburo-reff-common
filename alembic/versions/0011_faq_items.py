"""Add faq_items table for the admin "Материалы" panel, seeded with the
FAQ entries that used to be hardcoded in the site's faq.py.

Revision ID: 0011
Revises: 0010
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0011"
down_revision: str | Sequence[str] | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SCHEMA = "referral"

SEED_ITEMS = [
    (
        0,
        "Когда я получу деньги?",
        "Аванс начисляется, когда клиент подписывает договор. Основная выплата — когда "
        "клиент оплачивает депозит по делу. Статус каждой выплаты видно в вашем кабинете.",
    ),
    (
        1,
        "Как зафиксировать клиента за собой?",
        "Клиент закрепляется за вами автоматически, как только переходит по вашей "
        "персональной ссылке и оставляет заявку. Действует правило: кто зафиксировал "
        "клиента первым, тот и получает вознаграждение.",
    ),
    (
        2,
        "Что делать если человек уже обращался в Правбюро?",
        "Если по этому клиенту уже есть заявка от другого партнёра или он уже клиент "
        "Правбюро, новая заявка не создаст дубль — вознаграждение получит тот, кто "
        "зафиксировал клиента первым.",
    ),
    (
        3,
        "Как сформировать чек самозанятого?",
        "Чек формируется в приложении «Мой налог» на сумму полученной выплаты.",
    ),
    (
        4,
        "Как узнать на каком этапе мой клиент?",
        "Текущий статус по каждому клиенту виден в вашем кабинете.",
    ),
]


def upgrade() -> None:
    op.create_table(
        "faq_items",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("question", sa.String(300), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.bulk_insert(
        sa.table(
            "faq_items",
            sa.column("position", sa.Integer()),
            sa.column("question", sa.String()),
            sa.column("answer", sa.Text()),
            schema=SCHEMA,
        ),
        [
            {"position": position, "question": question, "answer": answer}
            for position, question, answer in SEED_ITEMS
        ],
    )


def downgrade() -> None:
    op.drop_table("faq_items", schema=SCHEMA)
