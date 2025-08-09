from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.security import generate_authcode
from app.schemas import auth_schema


async def send_authcode_by_email(db: AsyncSession, email: str) -> auth_schema.Authcode:
    """
    メールで認証コードを送信する。

    Parameters
    ----------
    db: AsyncSession
        DB接続
    email: str
        送信先メールアドレス

    Returns
    -------
    app.schames.auth_schema.Authcode
        認証コード
    """
    # authcode発行
    code: str = generate_authcode()
    authcode: auth_schema.Authcode = await crud.insert_authcode(db, email=email, code=code)

    # @TODO メール送信

    return authcode


async def verify_authcode(db: AsyncSession, authcode_id: str, code: str) -> auth_schema.Authcode:
    """
    認証コードを検証する。

    Parameters
    ----------
    db: AsyncSession
        DB接続
    authcode_id: str
        認証コードID
    code: str
        認証コード

    Returns
    -------
    app.schemas.auth_schema.Authcode:
        認証コード
    """
    result = await crud.select_authcode_by_id(db, authcode_id)

    # authcode_idが不正 または 認証コード不一致 の場合
    if result is None or result.code != code:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました。")
    # 有効期限切れの場合
    elif result.expire_datetime < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="有効期限が切れています。"
        )
    # 認証成功
    return result
