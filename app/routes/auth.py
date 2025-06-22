from fastapi import APIRouter, Depends
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.core.security import generate_authcode
from app.core.database import get_session
from app.schemas.auth import RequestIssueAuthcodeForEmail, ResponseIssueAuthcodeForEmail
from app.models import Authcode

router = APIRouter(tags=["auth"])

@router.post("/auth/email/issue-authcode", response_model=ResponseIssueAuthcodeForEmail)
async def issue_authcode_for_email(
    req: RequestIssueAuthcodeForEmail,
    db: AsyncSession = Depends(get_session)
  ) -> Any:
  # @TODO emailが登録済みでないかチェック

  # authcode発行
  code: str = generate_authcode()
  authcode: Authcode = await crud.insert_authcode(db, req, code)

  # @TODO メール送信

  return ResponseIssueAuthcodeForEmail(
      authcode_id=authcode.authcode_id,
      expire_datetime=authcode.expire_datetime
    )