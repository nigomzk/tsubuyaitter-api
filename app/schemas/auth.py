from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.config import get_settings


class CommonFields:
    """
    共通フィールド
    """

    delete_flag: bool | None = Field(..., title="削除フラグ")
    create_datetime: datetime | None = Field(..., title="作成日時")
    update_datetime: datetime | None = Field(..., title="更新日時")


class AuthcodeSchema(BaseModel, CommonFields):
    """
    認証コードスキーマ

    Args:
        BaseModel: Pydamic BaseModel
        CommonFields: 共通フィールド
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
