from __future__ import with_statement

import os
import sys
from logging.config import fileConfig

from sqlalchemy.engine import Engine
from sqlalchemy.schema import MetaData

from alembic import context
from app.db.base import postgres_metadata
from app.db.session import postgres_engine

parent_dir = os.path.abspath(os.getcwd())
sys.path.append(parent_dir)

config = context.config
fileConfig(config.config_file_name)


def render_item(obj_type, obj, autogen_context):
    """Apply custom rendering for selected items."""
    if obj_type == "type" and obj.__class__.__module__.startswith("sqlalchemy_utils."):
        autogen_context.imports.add(f"import {obj.__class__.__module__}")
        if hasattr(obj, "choices"):
            return f"{obj.__class__.__module__}.{obj.__class__.__name__}(choices={obj.choices})"
        else:
            return f"{obj.__class__.__module__}.{obj.__class__.__name__}()"

    # default rendering for other objects
    return False


class Migrator:
    def __init__(self, engine: Engine, target_metadata: MetaData) -> None:
        self.engine = engine
        self.target_metadata = target_metadata

    def migrate(self) -> None:
        connectable = config.attributes.get("connection", None)
        if connectable is None:
            connectable = self.engine.connect()
        context.configure(
            connection=connectable,
            target_metadata=self.target_metadata,
            compare_type=True,
            render_item=render_item,
        )
        with context.begin_transaction():
            self.prepare_migration_context()
            context.run_migrations()

    def prepare_migration_context(self) -> None:
        pass


class PostgresMigrator(Migrator):
    pass


def run_migrations_online() -> None:
    if config.config_ini_section == "postgres":
        migrator = PostgresMigrator(postgres_engine, postgres_metadata)

    migrator.migrate()


run_migrations_online()
