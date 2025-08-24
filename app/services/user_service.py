import secrets
import string

from fastapi import status
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core import security
from app.core.config import get_settings
from app.core.logger import AppLogger
from app.enums import IdentityType
from app.errors import ApiException
from app.schemas import user_schema

logger: AppLogger = AppLogger(f"{__name__}")


async def is_registered_email(db: AsyncSession, email: str) -> bool:
    """
    登録済みのメールアドレスか確認する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    email: str
        メールアドレス

    Returns
    -------
    result: bool
        True: 登録済み / False: 未登録
    """
    user_exist = await crud.select_user_by_email(db, email)
    return user_exist is not None


async def is_registered_username(db: AsyncSession, username: str) -> bool:
    """
    登録済みのユーザー名か確認する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    username: str
        ユーザー名

    Returns
    -------
    result: bool
        True: 登録済み / False: 未登録
    """
    user_exist = await crud.select_user_by_username(db, username)
    return user_exist is not None


async def generate_initial_username(db: AsyncSession) -> str:
    """
    ユニークな初期ユーザー名を生成する。

    Returns
    -------
    username: str
        初期ユーザー名
    """
    while True:
        username = "".join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(get_settings().USERNAME_MAX_LENGTH)
        )
        if not await is_registered_username(db, username):
            return username


async def set_password(
    db: AsyncSession, user_id: int, identity_types: list[IdentityType], password: SecretStr
) -> None:
    """
    パスワードを設定する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    user_id: int
        ユーザーID
    identity_types: list[str]
        識別子種別リスト
    password: pydantic.SecretStr
        パスワード
    """

    # ユーザー取得
    user = await crud.select_user_by_id(db, user_id)
    if not user:
        logger.error(f"ユーザーが存在しません。(user_id: {user_id})")
        raise ApiException(status_code=status.HTTP_400_BAD_REQUEST, msg="不正なリクエストです。")

    # パスワードをハッシュ化
    hashed_password = security.get_password_hash(password.get_secret_value())

    for identity_type in identity_types:
        # 登録済みの認証情報を取得
        user_credetial = await crud.select_user_credential_by_id_and_identity_type(
            db, user_id, identity_type.value
        )

        # 対象の識別子種別の認証情報が存在しない場合、認証情報を登録
        if user_credetial:
            await crud.update_user_credential_hashed_password(
                db, user_id, identity_type.value, hashed_password
            )

        # 対象の識別子種別の認証情報が存在する場合、認証情報を更新
        else:
            if identity_type == IdentityType.EMAIL:
                await crud.insert_user_credential(
                    db, user_id, IdentityType.EMAIL.value, user.email, hashed_password
                )
            elif identity_type == IdentityType.USERNAME:
                await crud.insert_user_credential(
                    db, user_id, IdentityType.USERNAME.value, user.username, hashed_password
                )


async def authenticate_user(db: AsyncSession, identity: str, password: str) -> user_schema.User:
    """
    認証に成功したユーザーを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    identity: str
        識別子
    password: str
        パスワード

    Returns
    -------
    User
        認証に成功したユーザー

    Raises
    ------
    HTTPException
        認証に失敗した場合
    """

    # 認証失敗時のエラー定義
    authentication_exception = ApiException(
        status_code=status.HTTP_400_BAD_REQUEST,
        msg="ユーザー名かパスワードが間違っています。",
    )

    # 認証情報取得
    user_credential = await crud.select_user_credential_by_identity(db, identity)
    if not user_credential:
        logger.error(f"ユーザー識別子が存在しません。(identity: {identity})")
        raise authentication_exception

    # 識別子種別ごとにユーザー取得方法を切り替え
    if user_credential.identity_type == IdentityType.USERNAME.value:
        user = await crud.select_user_by_username(db, identity)
    elif user_credential.identity_type == IdentityType.EMAIL.value:
        user = await crud.select_user_by_email(db, identity)
    else:
        logger.error(f"未定義の識別子種別です。(identity_type: {user_credential.identity_type})")
        raise authentication_exception

    # 対象ユーザー取得
    user = await crud.select_user_by_id(db, user_credential.user_id)
    if not user:
        # 外部キー制約のため、到達不可
        logger.error(f"ユーザーが存在しません。(user_id: {user_credential.user_id})")
        raise authentication_exception

    # パスワード検証
    if not security.verify_password(password, user_credential.hashed_password):
        logger.error(f"パスワードの検証に失敗しました。(user_id: {user_credential.user_id})")
        raise authentication_exception

    return user
