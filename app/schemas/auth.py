from pydantic import BaseModel, EmailStr, Field


class RequestIssueAuthcodeForEmail(BaseModel):
    """
    メール認証コード発行リクエスト
    """

    email: EmailStr = Field(..., title="メールアドレス")


class ResponseIssueAuthcodeForEmail(BaseModel):
    """
    メール認証コード発行レスポンス
    """

    authcode_id: str = Field(..., min_length=1, max_length=36, title="認証コードID")
    expire_datetime: str = Field(..., title="有効期限")
