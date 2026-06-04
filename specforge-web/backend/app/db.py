from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# Columns added after the initial schema. For local SQLite databases we apply
# these additively at startup so existing data is preserved without Alembic.
_ADDITIVE_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "runs": [("instruction_id", "INTEGER")],
    "artifacts": [("instruction_id", "INTEGER")],
    "test_runs": [("instruction_id", "INTEGER")],
}


async def _apply_additive_migrations(conn) -> None:
    def _migrate(sync_conn) -> None:
        from sqlalchemy import inspect

        inspector = inspect(sync_conn)
        existing_tables = set(inspector.get_table_names())
        for table, columns in _ADDITIVE_COLUMNS.items():
            if table not in existing_tables:
                continue
            present = {c["name"] for c in inspector.get_columns(table)}
            for name, ddl_type in columns:
                if name not in present:
                    sync_conn.execute(
                        text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl_type}")
                    )

    await conn.run_sync(_migrate)


async def init_db() -> None:
    async with engine.begin() as conn:
        # Import models so every table is registered on the metadata.
        import app.models  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)
        await _apply_additive_migrations(conn)
