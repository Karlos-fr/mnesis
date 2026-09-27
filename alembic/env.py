"""Configuration Alembic de Mnesis pour les migrations du schéma SQL."""

from alembic import context
from sqlalchemy import engine_from_config, pool

from mnesis.infrastructure.db import Base

config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Exécute les migrations sans ouvrir de connexion SQL persistante."""
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Exécute les migrations avec une connexion créée depuis la configuration."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
