import re

from app.core import security


def test_generate_authcode():
    """
    6桁数字文字列の認証コードが生成されること
    """
    authcode: str = security.generate_authcode()
    assert re.fullmatch(r"([0-9]{6})", authcode) is not None
