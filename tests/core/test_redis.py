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
