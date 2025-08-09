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
