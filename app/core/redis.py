from redis import ConnectionError
from redis.asyncio.client import Redis

from app.core.config import get_settings


async def get_redis_client() -> Redis:
    """
    Redisクライアントインスタンスを取得する
    """
    try:
        client = await Redis(
            host=get_settings().REDIS_HOST,
            port=get_settings().REDIS_PORT,
            db=get_settings().REDIS_DB,
            password=get_settings().REDIS_PASSWORD,
            decode_responses=True,
        )
        return client

    except ConnectionError as e:
        print(f"Redis接続エラー: {e}")
        raise


async def check_connection(redis: Redis) -> str:
    """
    Redisとの接続チェックを行う。
    """
    return await redis.ping()  # pyright: ignore[reportUnknownMemberType]
