from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Authcode
from app.schemas.auth import RequestIssueAuthcodeForEmail

async def insert_authcode(
    db: AsyncSession, 
    req: RequestIssueAuthcodeForEmail,
    code: str
  ) -> Authcode:
  """
  認証コードを登録する。

  Parameters
  ----------
  db: AsyncSession
    DB接続session
  req: RequestIssueAuthcodeForEmail
    メール認証コード発行リクエスト
  code: str
    コード
  
  Returns
  ----------
  authcode: Authcode
    登録結果
  """
  authcode = Authcode(email=req.email, code=code)
  db.add(authcode)
  await db.commit()
  await db.refresh(authcode)
  return authcode