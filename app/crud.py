from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Authcode
from app.schemas.auth import AuthcodeRead, AuthcodeSchema


async def insert_authcode(db: AsyncSession, email: str, code: str) -> Authcode:
    """
    認証コードを登録する。

    Parameters
    ----------
    db: AsyncSession
        DB接続session
    email: str
        メールアドレス
    code: str
        コード

    Returns
    ----------
    authcode: Authcode
        登録結果
    """
    authcode = Authcode(email=email, code=code)
    db.add(authcode)
    await db.commit()
    await db.refresh(authcode)
    return authcode


async def select_authcode_by_id(db: AsyncSession, data: AuthcodeRead) -> AuthcodeSchema | None:
    """
    認証コードIDで認証コードを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DB接続
    data: app.schemas.auth.AuthcodeRead
        読み取り用認証コードスキーマ

    Returns
    -------
    Authcode | None
        取得結果
    """
    result = (
        await db.scalars(select(Authcode).where(Authcode.authcode_id == data.authcode_id))
    ).first()
    return AuthcodeSchema(**result.__dict__) if result is not None else None
