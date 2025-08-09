from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums import Flag
from app.schemas.auth_schema import RequestVerifyAuthcode, ResponseIssueAuthcodeForEmail


class TempUser(BaseModel):
    """
    一時ユーザースキーマ
    """

    account_name: str
    email: EmailStr
    birthday: date

    # JSONからのデシリアライズ（str->date）のため実装
    @field_validator("birthday")
    @classmethod
    def iso_date(cls, value: str | date) -> date:
        return value if isinstance(value, date) else datetime.strptime(value, "%Y%m%d")


class User(BaseModel):
    """
    ユーザースキーマ
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    account_name: str
    email: EmailStr
    birthday: date
    self_introduction: str | None = None
    profile_image: str | None = None
    header_image: str | None = None
    verified_flag: str | Flag
    auth_failure_count: int
    account_lock_flag: str | Flag

    # JSONからのデシリアライズ（str->date）のため実装
    @field_validator("birthday")
    @classmethod
    def iso_date(cls, value: str | date) -> date:
        return value if isinstance(value, date) else datetime.strptime(value, "%Y%m%d")


class RequestRegisterUser(BaseModel):
    """
    ユーザー登録リクエストスキーマ
    """

    account_name: str = Field(..., min_length=1, max_length=50, title="アカウント名")
    email: EmailStr = Field(..., max_length=255, title="メールアドレス")
    birthday: date = Field(..., title="生年月日")


class ResponseRegisterUser(ResponseIssueAuthcodeForEmail):
    """
    ユーザー登録レスポンススキーマ
    """

    pass


class RequestUserVerifyAuthcode(RequestVerifyAuthcode):
    """
    ユーザー認証コード検証リクエストスキーマ
    """

    pass
