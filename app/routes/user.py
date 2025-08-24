import uuid
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Header, status
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core import email_manager, security
from app.core.config import get_settings
from app.core.database import get_session
from app.core.redis import generate_temp_user_key, get_redis_client
from app.errors import ApiException
from app.schemas import header_schema, request_schema, response_schema, token_schema
from app.schemas.user_schema import (
    TempUser,
)
from app.services import token_service, user_service

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user(
    req: request_schema.UserRegister,
    background_tasks: BackgroundTasks,
    headers: header_schema.CommonHeders = Header(),
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_client),
) -> response_schema.UserRegister:
    """
    ユーザー仮登録API
    """
    # メールアドレス重複チェック
    if await user_service.is_registered_email(db, req.email):
        raise ApiException(
            status_code=status.HTTP_400_BAD_REQUEST,
            msg="このメールアドレスはすでに利用されているため使用できません。",
        )

    # 受付ID、認証コード生成
    authcode = security.generate_authcode()
    reception_id = str(uuid.uuid4())
    temp_user = TempUser(**req.model_dump())
    await redis.setex(
        name=generate_temp_user_key(reception_id, authcode),
        time=timedelta(minutes=get_settings().AUTHCODE_EXPIRE_MINUTES),
        value=temp_user.model_dump_json(),
    )

    # メール送信
    context: dict[str, str | int] = {
        "code": authcode,
        "expire_miniutes": get_settings().AUTHCODE_EXPIRE_MINUTES,
        "message": "下記の認証コードを入力して、Tsubuyaitterへの登録を完了させてください。",
    }
    background_tasks.add_task(
        email_manager.send_email,
        [req.email],
        email_manager.TEMPLATE_CONTACT_AUTHCODE,
        "認証コードのご案内",
        context,
    )

    return response_schema.UserRegister(reception_id=reception_id)


@router.post("/register/verify-authcode", status_code=status.HTTP_200_OK)
async def verify_authcode(
    req: request_schema.UserRegisterVerifyAuthcode,
    headers: header_schema.CommonHeders = Header(),
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_client),
) -> token_schema.Token:
    """
    ユーザー登録認証コード検証API
    """

    # 認証コードの検証
    key = generate_temp_user_key(req.reception_id, req.authcode)
    data = await redis.get(key)
    if not data:
        raise ApiException(status_code=status.HTTP_401_UNAUTHORIZED, msg="認証に失敗しました。")
    temp_user = TempUser.model_validate_json(data)

    # キャッシュ上の一時ユーザー情報を削除
    await redis.delete(key)

    # メールアドレス重複チェック
    if await user_service.is_registered_email(db, temp_user.email):
        raise ApiException(
            status_code=status.HTTP_400_BAD_REQUEST,
            msg="問題が発生しました。最初からやり直してください。",
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


@router.post("/init-password", status_code=status.HTTP_200_OK)
async def init_password(
    req: request_schema.UserSetPassword,
    headers: header_schema.CommonHeders = Header(),
    db: AsyncSession = Depends(get_session),
) -> None:
    """
    ユーザーパスワード初期化API
    """
    await user_service.set_password(db, req.user_id, req.identity_types, req.password)
