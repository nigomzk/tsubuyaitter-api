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
