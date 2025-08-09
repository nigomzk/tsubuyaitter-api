import uuid
from datetime import datetime, timedelta

from jose import jwt
from redis.asyncio.client import Redis

from app.core.config import get_settings
from app.core.redis import generate_jwt_token_key
from app.schemas import token_schema, user_schema


async def create_token(
    user: user_schema.User,
    expires_delta: timedelta,
    redis: Redis,
) -> str:
    """
    JWTを作成する。

    Parameters
    ----------
    user: app.schemas.user_schema.User
        ユーザー
    expires_delta: timedelta
        有効期間（分）

    Returns
    -------
    str:
        JWT
    """
    # トークン生成
    token_id = str(uuid.uuid4())
    payload = token_schema.Payload(
        jti=token_id,
        iss=get_settings().BASE_URL,
        sub=str(user.user_id),
        exp=int(datetime.timestamp(datetime.now() + expires_delta)),
        nbf=int(datetime.timestamp(datetime.now())),
        iat=int(datetime.timestamp(datetime.now())),
    )
    token = jwt.encode(
        payload.model_dump(), get_settings().SECRET_KEY, algorithm=get_settings().ALGORITHM
    )

    # キャッシュに登録
    key = generate_jwt_token_key(token_id=token_id)
    await redis.setex(name=key, value=user.model_dump_json(), time=expires_delta)
    return token


async def create_access_token(user: user_schema.User, redis: Redis) -> str:
    """
    アクセストークンを作成する。

    Parameters
    ----------
    user: app.schemas.user_schema.User
        ユーザー

    Returns
    -------
    str:
        アクセストークン
    """
    access_token_expire = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    return await create_token(user=user, expires_delta=access_token_expire, redis=redis)


async def create_refresh_token(user: user_schema.User, redis: Redis) -> str:
    """
    リフレッシュトークンを作成する。

    Parameters
    ----------
    user: app.schemas.user_schema.User
        ユーザー

    Returns
    -------
    str:
        リフレッシュトークン
    """
    refresh_token_expire = timedelta(minutes=get_settings().REFRESH_TOKEN_EXPIRE_MINUTES)
    return await create_token(user=user, expires_delta=refresh_token_expire, redis=redis)


async def create_tokens(user: user_schema.User, redis: Redis) -> token_schema.Token:
    """
    トークンを発行する。

    Parameters
    ----------
    user: app.schemas.user_schema.User
        ユーザー

    Returns
    -------
    token_schema.Token
        トークンスキーマ
    """
    access_token = await create_access_token(user, redis)
    refresh_token = await create_refresh_token(user, redis)
    return token_schema.Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
