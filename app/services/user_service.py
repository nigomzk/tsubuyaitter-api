import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import get_settings


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
