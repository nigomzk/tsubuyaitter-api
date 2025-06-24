from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Authcode

async def insert_authcode(
    db: AsyncSession, 
    email: str,
    code: str
  ) -> Authcode:
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

async def select_authcode_by_id(db: AsyncSession, authcode_id: str) -> Optional[Authcode]:
  """
  認証コードを取得する。

  Parameters
  ----------
  db: AsyncSession
    DB接続session
  authcode_id: str
    認証コードID
  
  Returns
  ----------
  authcode: Optional[Authcode]
    取得結果
  """
  return db.query(Authcode).\
    filter_by(authcode_id=authcode_id).\
    one()
  