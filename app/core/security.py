import secrets
import string

from app.core.config import get_settings


def generate_authcode() -> str:
    """
    認証コードを生成する。

    Returns
    ----------
    authcode: str
        認証コード
    """
    return "".join(secrets.choice(string.digits) for _ in range(get_settings().AUTHCODE_LENGTH))
