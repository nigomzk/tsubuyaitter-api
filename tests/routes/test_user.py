from datetime import date, datetime, timedelta

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockFixture
from redis.asyncio.client import Redis
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import redis
from app.core.config import get_settings
from app.models import User
from app.schemas import auth_schema, user_schema


@pytest_asyncio.fixture
async def insert_test_temp_user(get_test_redis: Redis) -> None:
    """
    Redisにテスト用の一時ユーザーを登録する。

    +------------------------------------+------+------------------+----------------+----------+
    | authcode_id                        | code | account_name     | email          | birthday |
    +====================================+======+==================+================+==========+
    |00000000-0000-0000-0000-000000000000|123450|user0             |user0@sample.com|2000-01-01|
    +------------------------------------+------+------------------+----------------+----------+
    |00000000-0000-0000-0000-000000000001|123451|email_exists_in_db|user1@sample.com|2000-01-01|
    +------------------------------------+------+------------------+----------------+----------+
    """
    data: list[user_schema.TempUser] = [
        user_schema.TempUser(
            account_name="user0", email="user0@sample.com", birthday=date(2000, 1, 1)
        ),
        user_schema.TempUser(
            account_name="email_exists_in_db", email="user1@sample.com", birthday=date(2000, 1, 1)
        ),
    ]
    for i in range(len(data)):
        await get_test_redis.setex(
            redis.generate_temp_user_key(f"00000000-0000-0000-0000-00000000000{i}", f"12345{i}"),
            timedelta(minutes=get_settings().AUTHCODE_EXPIRE_MINUTES),
            data[i].model_dump_json(),
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["test_email", "is_success", "expected_http_status"],
    [
        # メールアドレス未使用のケース
        pytest.param("user9@sample.com", True, status.HTTP_200_OK),
        # メールアドレスが使用済みのケース
        pytest.param("user1@sample.com", False, status.HTTP_400_BAD_REQUEST),
    ],
)
async def test_register_user(
    mocker: MockFixture,
    async_client: AsyncClient,
    get_test_redis: Redis,
    insert_test_data_user: None,
    test_email: str,
    is_success: bool,
    expected_http_status: int,
):
    """
    ユーザー仮登録APIについて以下ケースを検証する。

    +----+-------------------------+------------------+-------------+
    | No | case                    | request email    | HTTP status |
    +====+=========================+==================+=============+
    | 1  | Success.                | user9@sample.com | 200         |
    +----+-------------------------+------------------+-------------+
    | 2  | Error(email duplicate). | user9@sample.com | 400         |
    +----+-------------------------+------------------+-------------+
    """
    # 認証コード生成をMock化
    test_authcode_id = "00000000-0000-0000-0000-000000000001"
    test_code = "123456"
    mocked_authcode = auth_schema.Authcode(
        authcode_id=test_authcode_id,
        code=test_code,
        email=test_email,
        expire_datetime=datetime.now(),
    )
    mocker.patch("app.services.auth_service.send_authcode_by_email", return_value=mocked_authcode)

    # テスト用リクエストデータ生成
    test_account_name = "テストユーザー"
    test_birthday = date(2000, 1, 1)
    reqest_data = {
        "account_name": test_account_name,
        "email": test_email,
        "birthday": test_birthday.strftime("%Y-%m-%d"),
    }

    # API呼び出し
    response = await async_client.post("/user/register", json=reqest_data)

    # HTTPステータスコードが期待通りであること
    assert response.status_code == expected_http_status

    # 正常時
    if is_success:
        # キャッシュに一時ユーザーが登録されていること
        response_obj = response.json()
        key = redis.generate_temp_user_key(response_obj["authcode_id"], test_code)
        data = await get_test_redis.get(key)
        chache_user = user_schema.TempUser.model_validate_json(data)
        assert chache_user.account_name == test_account_name
        assert chache_user.email == test_email
        assert chache_user.birthday == test_birthday
