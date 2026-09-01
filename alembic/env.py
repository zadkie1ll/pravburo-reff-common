from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.sql import text

from alembic import context
from pravburo_ref_common import models as application_models  # noqa: F401
from pravburo_ref_common.config import get_common_settings
from pravburo_ref_common.database import app_metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_common_settings()
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
target_metadata = app_metadata


def include_name(name: str | None, type_: str, parent_names: dict[str, str | None]) -> bool:
    """Inspect only Referral-owned objects in the dedicated referral database."""
    if type_ == "schema":
        return name == settings.referral_db_schema
    if type_ == "table":
        return parent_names.get("schema_name") == settings.referral_db_schema
    return True


def include_object(
    object_: object,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    del name, type_, compare_to
    schema = getattr(object_, "schema", None)
    return not reflected or schema == settings.referral_db_schema


def configure_context(connection: Connection | None = None) -> None:
    context.configure(
        connection=connection,
        url=None if connection is not None else settings.database_url,
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,
        include_object=include_object,
        compare_type=True,
        version_table="alembic_version_referral",
        version_table_schema=settings.referral_db_schema,
    )


def run_migrations_offline() -> None:
    configure_context()
    context.execute(f'CREATE SCHEMA IF NOT EXISTS "{settings.referral_db_schema}"')
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    configure_context(connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        # The Alembic version table itself belongs in the referral schema. Bootstrap
        # the namespace before Alembic tries to inspect that table.
        await connection.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{settings.referral_db_schema}"')
        )
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
