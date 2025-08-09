from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Authcode, User
from app.schemas import auth_schema, user_schema


async def check_connection(db: AsyncSession) -> None:
    """
    DB接続を確認する。

    Parameters
    ----------
    db: AsyncSession
        DB接続session
    """
    await db.scalars(select(1))
    return


async def insert_authcode(db: AsyncSession, email: str, code: str) -> auth_schema.Authcode:
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
    return auth_schema.Authcode(**authcode.__dict__)


async def select_authcode_by_id(db: AsyncSession, authcode_id: str) -> auth_schema.Authcode | None:
    """
    認証コードIDで認証コードを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DB接続
    authcode_id: str
        認証コードID

    Returns
    -------
    Authcode | None
        取得結果
    """
    result = (await db.scalars(select(Authcode).where(Authcode.authcode_id == authcode_id))).first()
    return auth_schema.Authcode(**result.__dict__) if result is not None else None


async def select_user_by_email(db: AsyncSession, email: str) -> user_schema.User | None:
    """
    メールアドレスでユーザーを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DB接続
    data: app.schemas.user.UserReadByEmail
        Read用ユーザースキーマ

    Returns
    -------
    User | None
        取得結果
    """
    result = (await db.scalars(select(User).where(User.email == email))).first()
    return user_schema.User(**result.__dict__) if result else None
