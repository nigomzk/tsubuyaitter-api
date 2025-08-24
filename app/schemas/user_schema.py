from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.enums import Flag


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


class UserCredential(BaseModel):
    """
    ユーザー認証情報スキーマ
    """

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    identity_type: str
    identity: str
    hashed_password: str
