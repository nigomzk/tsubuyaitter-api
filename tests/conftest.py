from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database import DATABASE_OPTION, Base, get_session
from app.main import app
from app.models import Authcode


@pytest_asyncio.fixture(scope="function")
async def get_test_session() -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    """
    テスト用のDB接続を取得する。
    """
    db_uri = (
        f"{get_settings().DATABASE_DIALECT}+{get_settings().DATABASE_ASYNC_DRIVER}://"
        f"{get_settings().TEST_DATABASE_USER}:"
        f"{quote_plus(get_settings().TEST_DATABASE_PASSWORD)}@"
        f"{get_settings().DATABASE_HOST}:{get_settings().DATABASE_PORT}/"
        f"{get_settings().TEST_DATABASE_NAME}"
    )
    engine: AsyncEngine = create_async_engine(db_uri, **DATABASE_OPTION)
    async_session = async_sessionmaker(
        engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=True,
    )
    # SQLAlchemyで定義しているテーブルを全て作成する
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield async_session


@pytest_asyncio.fixture(scope="function")
async def async_client(
    get_test_session: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, Any]:
    """
    テスト用の非同期HTTPクライアントを返却する。
    """

    async def _override_get_session():
        """
        DI override用の関数
        """
        async with get_test_session() as session:
            yield session

    # DIでFastAPIのDBの向き先をテスト用DBに変更
    app.dependency_overrides[get_session] = _override_get_session

    # テスト用非同期HTTPクライアントを返却
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def insert_test_data_authcode(get_test_session: async_sessionmaker[AsyncSession]) -> None:
    """
    認証コードテーブルに以下のデータを投入する。

    +------------+------------+-----------+-----------+-----------+
    | No | authcode_id | code | email | expire_datetime |
    +============+============+===========+===========+===========+
    |1|00000000-0000-0000-0000-000000000001|123451|test1@sample.com|2025-07-01 00:01:00.999999|
    +------------+------------+-----------+-----------+
    |2|00000000-0000-0000-0000-000000000002|123452|test2@sample.com|2025-07-01 00:02:00.999999|
    +------------+------------+-----------+-----------+
    |3|00000000-0000-0000-0000-000000000003|123453|test3@sample.com|2025-07-01 00:03:00.999999|
    +------------+------------+-----------+-----------+
    |4|00000000-0000-0000-0000-000000000004|123454|test4@sample.com|2025-07-01 00:04:00.999999|
    +------------+------------+-----------+-----------+
    |5|00000000-0000-0000-0000-000000000005|123455|test5@sample.com|2025-07-01 00:05:00.999999|
    +------------+------------+-----------+-----------+
    |6|00000000-0000-0000-0000-000000000006|123456|test6@sample.com|2025-07-01 00:06:00.999999|
    +------------+------------+-----------+-----------+

    Parameters
    ----------
    get_test_session: sqlalchemy.ext.asyncio.async_sessionmaker[AsyncSession]
        テスト用DBセッション
    """
    data = [
        Authcode(
            authcode_id=f"00000000-0000-0000-0000-00000000000{i}",
            code=f"12345{i}",
            email=f"test{i}@sample.com",
            expire_datetime=datetime.strptime(
                f"2025-07-01 00:0{i}:00.999999", "%Y-%m-%d %H:%M:%S.%f"
            ),
        )
        for i in range(1, 7)
    ]
    async with get_test_session() as db:
        db.add_all(data)
        await db.commit()
