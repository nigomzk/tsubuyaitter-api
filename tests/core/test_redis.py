import pytest

from app.core import redis


@pytest.mark.asyncio
async def test_get_redis_client() -> None:
    """
    Redisクライアントが取得できること。
    """
    client = await redis.get_redis_client()
    response = await client.ping()  # pyright: ignore[reportUnknownMemberType]
    assert response is not None


@pytest.mark.asyncio
async def test_check_connection() -> None:
    """
    Redisとの接続テストが成功すること。
    """
    client = await redis.get_redis_client()
    result = await redis.check_connection(client)
    assert result is not None


def test_generate_temp_user_key() -> None:
    """
    一時ユーザー用のRedisキーが以下形式で取得できること。

    "{Prefix}:{authcode_id}:{code}"
    """
    authcode_id = "00000000-0000-0000-0000-000000000001"
    code = "123456"
    expected = f"{redis.PREFIX_TEMP_USER}:{authcode_id}:{code}"
    result = redis.generate_temp_user_key(authcode_id=authcode_id, code=code)
    assert result == expected
