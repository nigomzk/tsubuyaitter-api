from collections.abc import AsyncGenerator
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

# DB接続先URL
DATABASE_URL: str = (
    f"{get_settings().DATABASE_DIALECT}+{get_settings().DATABASE_ASYNC_DRIVER}://"
    f"{get_settings().DATABASE_USER}:{quote_plus(get_settings().DATABASE_PASSWORD)}@"
    f"{get_settings().DATABASE_HOST}:{get_settings().DATABASE_PORT}/"
    f"{get_settings().DATABASE_NAME}"
)
# マイグレーション用DB接続先URL
MIGRATION_URL: str = (
    f"{get_settings().DATABASE_DIALECT}+{get_settings().DATABASE_DRIVER}://"
    f"{get_settings().DATABASE_USER}:{quote_plus(get_settings().DATABASE_PASSWORD)}@"
    f"{get_settings().DATABASE_HOST}:{get_settings().DATABASE_PORT}/"
    f"{get_settings().DATABASE_NAME}"
)
# DBオプション設定
DATABASE_OPTION: dict[str, bool | int] = {
    "echo": get_settings().SQL_LOGGING,
    "echo_pool": get_settings().SQL_LOGGING,
    "pool_size": get_settings().DATABASE_POOL_SIZE,
    "pool_timeout": get_settings().POOL_CONN_TIMEOUT,
    "max_overflow": get_settings().DATABASE_MAX_OVERFLOW,
    "pool_recycle": get_settings().POOL_RECYCLE,
    "pool_pre_ping": True,
}

Base = declarative_base()

engine: AsyncEngine = create_async_engine(DATABASE_URL, **DATABASE_OPTION)
async_session = async_sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,
)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    DB sessionを取得する
    """
    async with async_session() as session:
        yield session
