from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Authcode


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
