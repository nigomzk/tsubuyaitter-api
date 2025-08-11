import pytest
from fastapi_mail import FastMail

from app.core import email_manager
from app.core.config import get_settings


@pytest.fixture
def test_fm() -> FastMail:
    """
    メール送信を抑止する
    """
    fm = email_manager.fm
    fm.config.SUPPRESS_SEND = 1
    return fm


@pytest.mark.asyncio
async def test_send_email_by_contact_authcode(test_fm: FastMail):
    """
    send_email (テンプレートcontact_authcode.html使用時) の検証
    """

    # テンプレートcontact_authcode.html用設定
    send_to = "test@sample.com"
    test_template = email_manager.TEMPLATE_CONTACT_AUTHCODE
    test_subject = "認証コードのご案内"
    test_context: dict[str, str | int] = {
        "code": "123456",
        "expire_miniutes": 10,
        "message": "下記の認証コードを入力して、Tsubuyaitterへの登録を完了させてください。",
    }

    with test_fm.record_messages() as outbox:  # pyright: ignore[reportUnknownVariableType]
        # メール送信実行
        await email_manager.send_email(
            emails=[send_to],
            template_name=test_template,
            subject=test_subject,
            context=test_context,
        )
        assert len(outbox) == 1  # pyright: ignore[reportUnknownArgumentType]
        assert outbox[0]["from"] == get_settings().MAIL_FROM
        assert outbox[0]["to"] == send_to
