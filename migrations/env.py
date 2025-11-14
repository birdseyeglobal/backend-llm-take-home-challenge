# Importing alembic_postgresql_enum ensures that the extension is used
import os

import alembic_postgresql_enum  # noqa: F401
from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool, text

from app.base.config import settings  # Ensure alembic uses the app logger
from app.base.db.models import SQLModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url() -> str:
    if not os.getenv("DISABLE_DOTENV") == "1":
        load_dotenv()
    return settings.SQLALCHEMY_DATABASE_URI


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is not None:
        configuration["sqlalchemy.url"] = get_url()
    else:
        raise ValueError("configuration is None")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            connection.execute(
                text("SELECT pg_advisory_xact_lock(10000);"),
            )  # prevent concurrent migrations
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
