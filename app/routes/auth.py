from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.database import get_session
from app.core.security import generate_authcode
from app.models import Authcode
from app.schemas.auth import RequestIssueAuthcodeForEmail, ResponseIssueAuthcodeForEmail

router = APIRouter(tags=["auth"])


@router.post("/auth/email/issue-authcode", response_model=ResponseIssueAuthcodeForEmail)
async def issue_authcode_for_email(
    req: RequestIssueAuthcodeForEmail, db: AsyncSession = Depends(get_session)
) -> Any:
    """
    メール認証コード発行API

    Args:
        req (RequestIssueAuthcodeForEmail): リクエスト
        db (AsyncSession, optional): Defaults to Depends(get_session).

    Returns:
        Any: レスポンス
    """
    # @TODO emailが登録済みでないかチェック

    # authcode発行
    code: str = generate_authcode()
    authcode: Authcode = await crud.insert_authcode(db, req.email, code)

    # @TODO メール送信

    return ResponseIssueAuthcodeForEmail(
        authcode_id=str(authcode.authcode_id),
        expire_datetime=str(authcode.expire_datetime),
    )
