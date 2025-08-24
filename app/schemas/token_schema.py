from pydantic import BaseModel, SecretStr, field_serializer


class Payload(BaseModel):
    """
    ペイロードスキーマ
    """

    jti: str  # token id
    iss: str  # base url
    sub: str  # user id
    exp: int  # expiration time
    nbf: int  # not before
    iat: int  # issued at


class Token(BaseModel):
    """
    トークンスキーマ
    """

    access_token: SecretStr
    refresh_token: SecretStr
    token_type: str = "bearer"

    @field_serializer("access_token", "refresh_token", when_used="json")
    def dump_secret(self, v: SecretStr):
        return v.get_secret_value()
