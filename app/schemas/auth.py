from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.config import get_settings
from app.schemas.base import BaseSechemaMixin


class AuthcodeSchema(BaseSechemaMixin):
    """
    認証コードスキーマ

    Attributes
    ----------
    authcode_id: str
        認証コードID
    code: str
        認証コード
    email: pydantic.EmailStr
        メールアドレス
    expire_datetime: datetime.datetime
        有効期限
    """

    authcode_id: str = Field(..., min_length=36, max_length=36, title="認証コードID")
    code: str = Field(
        ...,
        min_length=get_settings().AUTHCODE_LENGTH,
        max_length=get_settings().AUTHCODE_LENGTH,
        title="認証コード",
    )
    email: EmailStr = Field(..., title="メールアドレス")
    expire_datetime: datetime = Field(..., title="有効期限")

    class ConfigDict:
        from_attributes = True


class AuthcodeRead(BaseModel):
    """
    Read用認証コードスキーマ

    Attributes
    ----------
    authcode_id: str
        認証コードID
    """

    authcode_id: str = Field(...)


class RequestIssueAuthcodeForEmail(BaseModel):
    """
    メール認証コード発行リクエスト
    """

    email: EmailStr = Field(..., title="メールアドレス")


class ResponseIssueAuthcodeForEmail(BaseModel):
    """
    メール認証コード発行レスポンス
    """

    authcode_id: str = Field(..., min_length=36, max_length=36, title="認証コードID")
    expire_datetime: str = Field(..., title="有効期限")


class RequestVerifyAuthcode(BaseModel):
    """
    認証コード検証リクエスト

    Attributes
    ----------
    authcode_id: str
        認証コードID
    code: str
        認証コード
    """

    authcode_id: str = Field(..., min_length=36, max_length=36, title="認証コードID")
    code: str = Field(
        ...,
        min_length=get_settings().AUTHCODE_LENGTH,
        max_length=get_settings().AUTHCODE_LENGTH,
        title="認証コード",
    )
