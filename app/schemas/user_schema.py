from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

from app.core.config import get_settings
from app.enums import Flag, IdentityType


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


class RequestRegisterUser(BaseModel):
    """
    ユーザー登録リクエストスキーマ
    """

    account_name: str = Field(..., min_length=1, max_length=50, title="アカウント名")
    email: EmailStr = Field(..., max_length=255, title="メールアドレス")
    birthday: date = Field(..., title="生年月日")


class ResponseRegisterUser(BaseModel):
    """
    ユーザー登録レスポンススキーマ
    """

    reception_id: str = Field(..., min_length=36, max_length=36, title="受付ID")


class RequestRegisterUserVerifyAuthcode(BaseModel):
    """
    ユーザー認証コード検証リクエストスキーマ
    """

    reception_id: str = Field(..., min_length=36, max_length=36, title="受付ID")
    authcode: str = Field(
        ...,
        min_length=get_settings().AUTHCODE_LENGTH,
        max_length=get_settings().AUTHCODE_LENGTH,
        title="認証コード",
    )


class RequestSetPassword(BaseModel):
    """
    パスワード設定リクエストスキーマ
    """

    user_id: int = Field(..., title="ユーザーID")
    identity_types: list[IdentityType] = Field(..., title="識別子種別")
    password: SecretStr = Field(..., title="パスワード")

    @field_validator("identity_types")
    def validate_identity_types(cls, values: list[IdentityType]) -> list[IdentityType]:
        if len(values) == 0:
            raise ValueError("識別子種別が設定されていません。")
        for value in values:
            if value != IdentityType.EMAIL and value != IdentityType.USERNAME:
                raise ValueError("識別子種別が不正です。")
        return values

    @field_validator("password")
    def validate_password(cls, value: SecretStr) -> SecretStr:
        min_length = get_settings().PASSWORD_MIN_LENGTH
        max_length = get_settings().PASSWORD_MAX_LENGTH
        special_symbols = list(get_settings().PASSWORD_VALID_SPECIAL_SYMBOL)

        # パスワード文字数チェック
        if len(value.get_secret_value()) < min_length or len(value.get_secret_value()) > max_length:
            raise ValueError(f"パスワードは{min_length}文字以上、{max_length}文字以下です。")
        # パスワードは半角数字を最低1文字含む
        if not any(char.isdigit() for char in value.get_secret_value()):
            raise ValueError("パスワードは最低1文字は数字(0-9)が必要です。")
        # パスワードは大文字を最低1文字含む
        if not any(char.isupper() for char in value.get_secret_value()):
            raise ValueError("パスワードは最低1文字は大文字(A-Z)が必要です。")
        # パスワードは小文字を最低1文字含む
        if not any(char.islower() for char in value.get_secret_value()):
            raise ValueError("パスワードは最低1文字は小文字(a-z)が必要です。")
        # パスワードは記号を最低1文字含む
        if not any(char in special_symbols for char in value.get_secret_value()):
            raise ValueError(f"パスワードは最低1文字は記号 ({special_symbols}) が必要です。")

        return value
