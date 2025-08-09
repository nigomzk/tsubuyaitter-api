from pydantic import BaseModel


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

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
