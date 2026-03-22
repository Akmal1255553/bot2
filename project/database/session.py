from collections.abc import AsyncIterator

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from config import get_settings
from database.models import Base

settings = get_settings()

_engine_kwargs: dict = {"echo": False}
if "sqlite" in settings.database_url:
    _engine_kwargs["poolclass"] = StaticPool
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_pre_ping"] = True
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20

engine: AsyncEngine = create_async_engine(settings.database_url, **_engine_kwargs)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_users_schema(conn)


async def _ensure_users_schema(conn) -> None:
    def _get_columns(sync_conn) -> set[str]:
        inspector = inspect(sync_conn)
        table_names = set(inspector.get_table_names())
        if "users" not in table_names:
            return set()
        return {column["name"] for column in inspector.get_columns("users")}

    existing_columns = await conn.run_sync(_get_columns)
    if not existing_columns:
        return

    dialect = conn.dialect.name
    timestamp_type = "TIMESTAMPTZ" if dialect == "postgresql" else "TIMESTAMP"
    add_column_statements: list[str] = []

    if "language" not in existing_columns:
        add_column_statements.append("ALTER TABLE users ADD COLUMN language VARCHAR(2)")
    if "usage_period_started_at" not in existing_columns:
        add_column_statements.append(
            f"ALTER TABLE users ADD COLUMN usage_period_started_at {timestamp_type} NULL"
        )
    if "request_window_started_at" not in existing_columns:
        add_column_statements.append(
            f"ALTER TABLE users ADD COLUMN request_window_started_at {timestamp_type} NULL"
        )
    if "requests_in_window" not in existing_columns:
        add_column_statements.append(
            "ALTER TABLE users ADD COLUMN requests_in_window INTEGER NOT NULL DEFAULT 0"
        )

    for statement in add_column_statements:
        await conn.execute(text(statement))

    await conn.execute(
        text(
            "UPDATE users SET usage_period_started_at = CURRENT_TIMESTAMP "
            "WHERE usage_period_started_at IS NULL"
        )
    )
    await conn.execute(
        text(
            "UPDATE users SET request_window_started_at = CURRENT_TIMESTAMP "
            "WHERE request_window_started_at IS NULL"
        )
    )
    await conn.execute(
        text("UPDATE users SET requests_in_window = 0 WHERE requests_in_window IS NULL")
    )
    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_language ON users(language)"))


async def close_db() -> None:
    await engine.dispose()
