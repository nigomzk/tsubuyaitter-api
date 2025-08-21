from collections.abc import AsyncGenerator, Sequence
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.expression import ClauseElement

from app.core.config import get_settings
from app.core.logger import AppLogger

# ロガー設定
logger: AppLogger = AppLogger(__name__)

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


@event.listens_for(engine.sync_engine, "before_execute")
def logging_before_execute(
    conn: Connection,
    clause_element: ClauseElement,
    multiparams: Sequence[dict[str, Any]] | None = None,
    params: dict[str, Any] | None = None,
    execution_options: dict[str, Any] | None = None,
) -> None:
    """
    実行するSQLをログ出力するイベントリスナー

    Parameters
    ----------
    async_session: AsyncGenerator[AsyncSession, Any])
        DBセッション
    clause_element: ClauseElement
        SQL式構造
    multiparams: Sequence[dict[str, Any]] | None
        複数のバインドパラメータセット
    params: dict[str, Any] | None
        単一のバインドパラメータセット
    execution_options: dict[str, Any] | None
        実行オプション
    """
    compiled = clause_element.compile(dialect=engine.dialect)
    logger.info(f"{compiled}")
    if compiled.params:
        logger.debug(str(compiled.params))
