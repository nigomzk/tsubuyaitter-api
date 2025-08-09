from collections.abc import AsyncGenerator
from datetime import date, datetime
from typing import Any
from urllib.parse import quote_plus

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis import ConnectionError
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database import DATABASE_OPTION, Base, get_session
from app.core.redis import get_redis_client
from app.main import app
from app.models import Authcode, User


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
        await conn.run_sync(Base.metadata.create_all)

    yield async_session

    # SQLAlchemyで定義しているテーブルを全て削除する
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def get_test_redis() -> Redis:
    """
    テスト用Redisクライアントインスタンスを取得する
    """
    try:
        client = await Redis(
            host=get_settings().REDIS_HOST,
            port=get_settings().REDIS_PORT,
            db=get_settings().TEST_REDIS_DB,
            password=get_settings().REDIS_PASSWORD,
            decode_responses=True,
        )
        # テスト用DBを初期化
        await client.flushdb()  # pyright: ignore[reportUnknownMemberType]

        return client

    except ConnectionError as e:
        print(f"Redis接続エラー: {e}")
        raise


@pytest_asyncio.fixture(scope="function")
async def async_client(
    get_test_session: async_sessionmaker[AsyncSession],
    get_test_redis: Redis,
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

    async def _ovveride_get_redis():
        return get_test_redis

    # DIでFastAPIのDBの向き先をテスト用DBに変更
    app.dependency_overrides[get_session] = _override_get_session
    app.dependency_overrides[get_redis_client] = _ovveride_get_redis

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


@pytest_asyncio.fixture(scope="function")
async def insert_test_data_user(get_test_session: async_sessionmaker[AsyncSession]) -> None:
    """
    ユーザーテーブルに以下のデータを投入する。

    +-------+--------+------------+-----+--------+-------------+-------------------+-----------------+
    |user_id|username|account_name|email|birthday|verified_flag|auth_failture_count|account_lock_flag|
    +=======+========+============+=====+========+=============+===================+=================+
    |1|user1|ユーザー1|user1@sample.com|2000-01-01|1|1|0|
    +-------+--------+------------+-----+-------+-------------+--------------------+-----------------+
    |2|user2|ユーザー2|user2@sample.com|2000-01-01|0|2|0|
    +-------+--------+------------+-----+-------+-------------+--------------------+-----------------+
    |3|user3|ユーザー3|user3@sample.com|2000-01-01|1|3|0|
    +-------+--------+------------+-----+-------+-------------+--------------------+-----------------+

    Parameters
    ----------
    get_test_session: sqlalchemy.ext.asyncio.async_sessionmaker[AsyncSession]
        テスト用DBセッション
    """
    data = [
        User(
            username=f"user{i}",
            account_name=f"ユーザー{i}",
            email=f"user{i}@sample.com",
            birthday=date(2000, 1, i),
            verified_flag=str(i % 2),
            auth_failure_count=(i % 5),
            account_lock_flag="0" if i < 5 else "1",
        )
        for i in range(1, 4)
    ]
    async with get_test_session() as db:
        db.add_all(data)
        await db.commit()
