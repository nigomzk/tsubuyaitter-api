from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import user_schema


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


async def select_user_by_username(db: AsyncSession, username: str) -> user_schema.User | None:
    """
    ユーザー名でユーザーを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    username: str
        ユーザー名

    Returns
    -------
    User | None
        取得結果
    """
    result = (await db.scalars(select(User).where(User.username == username))).first()
    return user_schema.User(**result.__dict__) if result else None


async def insert_user(
    db: AsyncSession, username: str, account_name: str, email: str, birthday: date
) -> user_schema.User:
    """
    ユーザーを登録する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    username: str
        ユーザー名
    account_name: str
        アカウント名（表示名）
    email: str
        メールアドレス
    birthday: datetime.date
        誕生日

    Returns
    -------
    app.schemas.user.UserSchema:
        登録結果
    """
    user = User(username=username, account_name=account_name, email=email, birthday=birthday)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user_schema.User(**user.__dict__)
