import secrets
import string

from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_authcode() -> str:
    """
    認証コードを生成する。

    Returns
    ----------
    authcode: str
        認証コード
    """
    return "".join(secrets.choice(string.digits) for _ in range(get_settings().AUTHCODE_LENGTH))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証する。

    Parameters
    ----------
    plain_password: str
        パスワード
    hashed_password: str
        ハッシュ化済みパスワード
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する。
    """
    return pwd_context.hash(password)
