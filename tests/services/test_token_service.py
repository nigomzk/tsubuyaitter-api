from datetime import date, datetime, timedelta

import pytest
from freezegun import freeze_time
from jose import jwt
from redis.asyncio.client import Redis

from app.core.config import get_settings
from app.core.redis import generate_jwt_token_key
from app.schemas import token_schema, user_schema
from app.services import token_service


@pytest.fixture()
def test_user() -> user_schema.User:
    return user_schema.User(
        user_id=1,
        username="test_user",
        account_name="テストユーザー",
        email="test_user@sample.com",
        birthday=date(year=2000, month=1, day=1),
        verified_flag="0",
        auth_failure_count=0,
        account_lock_flag="0",
    )


@freeze_time("2025-07-01 00:00:00")
@pytest.mark.asyncio
async def test_create_token(test_user: user_schema.User, get_test_redis: Redis):
    """
    create_tokenでJWTトークンの生成、キャッシュへの保存が正しく実行されること。
    """

    # 有効期限設定
    expire_delta = 10
    expire_datetime = datetime.strptime("2025-07-01 00:10:00", "%Y-%m-%d %H:%M:%S")
    expire_timestamp = int(datetime.timestamp(expire_datetime))

    # JWTトークンからpayload、キャッシュデータを取得
    token = await token_service.create_token(
        test_user, timedelta(minutes=expire_delta), get_test_redis
    )
    decoded_data = jwt.decode(
        token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
    )
    payload = token_schema.Payload(**decoded_data)
    data = await get_test_redis.get(generate_jwt_token_key(payload.jti))
    chache_user = user_schema.User.model_validate_json(data)

    # payloadに設定されたuser_id、有効期限が正しいこと
    assert payload.sub == str(test_user.user_id)
    assert payload.exp == expire_timestamp
    # キャッシュに保存されたユーザー情報が正しいこと
    assert chache_user.__dict__ == test_user.__dict__


@freeze_time("2025-07-01 00:00:00")
@pytest.mark.asyncio
async def test_create_access_token(test_user: user_schema.User, get_test_redis: Redis):
    """
    create_access_tokenでJWTトークンの生成、キャッシュへの保存が正しく実行されること。
    """

    # 有効期限
    expected_expire = int(
        datetime.timestamp(
            datetime.now() + timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )

    # JWTトークンからpayload、キャッシュデータを取得
    token = await token_service.create_access_token(test_user, get_test_redis)
    decoded_data = jwt.decode(
        token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
    )
    payload = token_schema.Payload(**decoded_data)
    data = await get_test_redis.get(generate_jwt_token_key(payload.jti))
    chache_user = user_schema.User.model_validate_json(data)

    # payloadに設定されたuser_id、有効期限が正しいこと
    assert payload.sub == str(test_user.user_id)
    assert payload.exp == expected_expire
    # キャッシュに保存されたユーザー情報が正しいこと
    assert chache_user.__dict__ == test_user.__dict__


@freeze_time("2025-07-01 00:00:00")
@pytest.mark.asyncio
async def test_create_refresh_token(test_user: user_schema.User, get_test_redis: Redis):
    """
    create_refresh_tokenでJWTトークンの生成、キャッシュへの保存が正しく実行されること。
    """

    # 有効期限
    expected_expire = int(
        datetime.timestamp(
            datetime.now() + timedelta(minutes=get_settings().REFRESH_TOKEN_EXPIRE_MINUTES)
        )
    )

    # JWTトークンからpayload、キャッシュデータを取得
    token = await token_service.create_refresh_token(test_user, get_test_redis)
    decoded_data = jwt.decode(
        token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
    )
    payload = token_schema.Payload(**decoded_data)
    data = await get_test_redis.get(generate_jwt_token_key(payload.jti))
    chache_user = user_schema.User.model_validate_json(data)

    # payloadに設定されたuser_id、有効期限が正しいこと
    assert payload.sub == str(test_user.user_id)
    assert payload.exp == expected_expire
    # キャッシュに保存されたユーザー情報が正しいこと
    assert chache_user.__dict__ == test_user.__dict__


@freeze_time("2025-07-01 00:00:00")
@pytest.mark.asyncio
async def test_create_tokens(test_user: user_schema.User, get_test_redis: Redis):
    """
    create_tokensでアクセストークン、リフレッシュトークンの生成、キャッシュへの保存が正しく実行されること。
    """
    # アクセストークン有効期限
    expected_expire_at = int(
        datetime.timestamp(
            datetime.now() + timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )
    # リフレッシュトークン有効期限
    expected_expire_rt = int(
        datetime.timestamp(
            datetime.now() + timedelta(minutes=get_settings().REFRESH_TOKEN_EXPIRE_MINUTES)
        )
    )

    # create_tokens実行
    token = await token_service.create_tokens(test_user, get_test_redis)

    # アクセストークンからpayload、キャッシュデータを取得
    access_token = jwt.decode(
        token.access_token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
    )
    payload_at = token_schema.Payload(**access_token)
    data_at = await get_test_redis.get(generate_jwt_token_key(payload_at.jti))
    chache_user_at = user_schema.User.model_validate_json(data_at)

    # リフレッシュトークンからpayload、キャッシュデータを取得
    refresh_token = jwt.decode(
        token.refresh_token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM]
    )
    payload_rt = token_schema.Payload(**refresh_token)
    data_rt = await get_test_redis.get(generate_jwt_token_key(payload_rt.jti))
    chache_user_rt = user_schema.User.model_validate_json(data_rt)

    # アクセストークンのpayloadに設定されたuser_id、有効期限が正しいこと
    assert payload_at.sub == str(test_user.user_id)
    assert payload_at.exp == expected_expire_at
    # アクセストークンのキャッシュに保存されたユーザー情報が正しいこと
    assert chache_user_at.__dict__ == test_user.__dict__

    # リフレッシュトークンのpayloadに設定されたuser_id、有効期限が正しいこと
    assert payload_rt.sub == str(test_user.user_id)
    assert payload_rt.exp == expected_expire_rt
    # リフレッシュトークンのキャッシュに保存されたユーザー情報が正しいこと
    assert chache_user_rt.__dict__ == test_user.__dict__
