from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.database import get_session
from app.schemas import auth_schema
from app.services.auth_service import send_authcode_by_email

router = APIRouter(tags=["auth"])


@router.post("/auth/email/issue-authcode", response_model=auth_schema.ResponseIssueAuthcodeForEmail)
async def issue_authcode_for_email(
    req: auth_schema.RequestIssueAuthcodeForEmail, db: AsyncSession = Depends(get_session)
) -> Any:
    """
    メール認証コード発行API

    Args:
        req (RequestIssueAuthcodeForEmail): リクエスト
        db (AsyncSession, optional): Defaults to Depends(get_session).

    Returns:
        Any: レスポンス
    """

    # authcode発行、メール送信
    authcode: auth_schema.Authcode = await send_authcode_by_email(db, req.email)

    return auth_schema.ResponseIssueAuthcodeForEmail(
        authcode_id=authcode.authcode_id, expire_datetime=authcode.expire_datetime
    )


@router.post("/auth/verify-authcode", response_model=None, status_code=status.HTTP_200_OK)
async def verify_authcode(
    req: auth_schema.RequestVerifyAuthcode, db: AsyncSession = Depends(get_session)
) -> None:
    """
    認証コード検証API

    Parameters
    ----------
    req: auth.RequestVerifyAuthcode
        認証コード検証リクエスト
    db: AsyncSession, optional)
        DBセッション Defaults to Depends(get_session).

    Raises
    ------
    HTTPException:
        authcode_idが不正 または 認証コード不一致 の場合（HTTPステータスコード：401）
    HTTPException:
        有効期限切れの場合（HTTPステータスコード：403）
    """

    result = await crud.select_authcode_by_id(db, req.authcode_id)

    # authcode_idが不正 または 認証コード不一致 の場合
    if result is None or result.code != req.code:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証に失敗しました。")
    # 有効期限切れの場合
    elif result.expire_datetime < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="有効期限が切れています。"
        )
    # 認証成功
    return
