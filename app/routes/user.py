from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import get_settings
from app.core.database import get_session
from app.core.redis import generate_temp_user_key, get_redis_client
from app.schemas import token_schema
from app.schemas.auth_schema import Authcode
from app.schemas.user_schema import (
    RequestRegisterUser,
    RequestVerifyAuthcode,
    ResponseRegisterUser,
    TempUser,
)
from app.services import auth_service, token_service, user_service

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user(
    req: RequestRegisterUser,
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_client),
) -> ResponseRegisterUser:
    """
    ユーザー仮登録API
    """
    # メールアドレス重複チェック
    if await user_service.is_registered_email(db, req.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスはすでに利用されているため使用できません。",
        )

    # 認証コード生成、メール送信
    authcode: Authcode = await auth_service.send_authcode_by_email(db, req.email)
    temp_user = TempUser(**req.model_dump())
    key = generate_temp_user_key(authcode.authcode_id, authcode.code)
    await redis.setex(
        key,
        timedelta(minutes=get_settings().AUTHCODE_EXPIRE_MINUTES),
        temp_user.model_dump_json(),
    )

    return ResponseRegisterUser(
        authcode_id=authcode.authcode_id, expire_datetime=authcode.expire_datetime
    )


@router.post("/register/verify-authcode", status_code=status.HTTP_200_OK)
async def verify_authcode(
    req: RequestVerifyAuthcode,
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_client),
) -> token_schema.Token:
    """
    ユーザー登録認証コード検証API
    """

    # 認証コードの検証
    key = generate_temp_user_key(req.authcode_id, req.code)
    data = await redis.get(key)
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました。")
    temp_user = TempUser.model_validate_json(data)

    # キャッシュ上の一時ユーザー情報を削除
    await redis.delete(key)

    # メールアドレス重複チェック
    if await user_service.is_registered_email(db, temp_user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="問題が発生しました。最初からやり直してください。",
        )

    # ユニークな初期ユーザー名の生成
    initial_username = await user_service.generate_initial_username(db)

    # ユーザー登録
    user = await crud.insert_user(
        db,
        username=initial_username,
        account_name=temp_user.account_name,
        email=temp_user.email,
        birthday=temp_user.birthday,
    )

    # JWTトークンを返却
    return await token_service.create_tokens(user, redis)
