"""Alembic environment.

The URL (`migration_database_url`, the owner's) comes from `Settings`, never from
`alembic.ini` — a committed connection string is both a secret-handling problem (R3) and a
way to migrate the wrong database.

FR-435: migrations run as an explicit pre-deploy step, never automatically on
application start. Nothing here is invoked by `create_app`.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import load_settings
from app.db import models as _models  # noqa: F401  — registers the tables on Base.metadata
from app.db.base import Base

config = context.config
if config.config_file_name is not None:
    # `disable_existing_loggers=False`: alembic can run in-process (the test suite does), and
    # the default would disable every logger that already exists, the application's
    # included, for the rest of the process.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata
_migration_url = load_settings().migration_database_url
if _migration_url is None:
    # Migrations run as the owner, never as the application's login role (FD-1729): falling
    # back to `GIP_DATABASE_URL` would run DDL as a role that cannot, or worse, as one that can.
    raise RuntimeError(
        "GIP_MIGRATION_DATABASE_URL is not set: migrations run as the schema owner and never "
        "fall back to GIP_DATABASE_URL (the application's login role)"
    )
config.set_main_option("sqlalchemy.url", _migration_url.get_secret_value())


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
