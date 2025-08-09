from redis import ConnectionError
from redis.asyncio.client import Redis

from app.core.config import get_settings

# キーの用途別prefix定義
PREFIX_TEMP_USER = "temp_user"
PREFIX_JWT_TOKEN = "jwt_token"


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


def generate_temp_user_key(authcode_id: str, code: str) -> str:
    """
    一時ユーザー用キーを生成する。

    Parameters
    ----------
    authcode_id: str
        認証コードID
    code: str
        認証コード

    Returns
    -------
    str:
        一時ユーザー用キー
    """
    return f"{PREFIX_TEMP_USER}:{authcode_id}:{code}"


def generate_jwt_token_key(token_id: str) -> str:
    """
    JWTトークン用キーを生成する。

    Parameters
    ----------
    token_id: str
        トークンID

    Returns
    -------
    str:
        JWTトークン用キー
    """
    return f"{PREFIX_JWT_TOKEN}:{token_id}"
