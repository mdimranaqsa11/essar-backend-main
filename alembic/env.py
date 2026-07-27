import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.models  # noqa: F401 - registers all models onto Base.metadata
from app.core.config import settings
from app.db.base import Base

# Step 1: tell alembic "yaha se DB ka URL milega" (.env se aata hai)
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Step 2: tell alembic "yaha models ki list hai, ismein compare karna hai DB se"
target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": "require"},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


asyncio.run(run_migrations())
