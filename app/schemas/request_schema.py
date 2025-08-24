from datetime import date

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator

from app.core.config import get_settings
from app.enums import IdentityType


class UserRegister(BaseModel):
    """
    ユーザー登録リクエストスキーマ
    """

    account_name: str = Field(..., min_length=1, max_length=50, title="アカウント名")
    email: EmailStr = Field(..., max_length=255, title="メールアドレス")
    birthday: date = Field(..., title="生年月日")


class UserRegisterVerifyAuthcode(BaseModel):
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


class UserSetPassword(BaseModel):
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
