from pathlib import Path
from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import SecretStr

from app.core.config import get_settings

# メールテンプレート名定義
TEMPLATE_CONTACT_AUTHCODE = "contact_authcode.html"

# メール設定
conf = ConnectionConfig(
    MAIL_USERNAME=get_settings().MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(get_settings().MAIL_PASSWORD),
    MAIL_FROM=get_settings().MAIL_FROM,
    MAIL_PORT=get_settings().MAIL_PORT,
    MAIL_SERVER=get_settings().MAIL_SERVER,
    MAIL_STARTTLS=get_settings().MAIL_STARTTLS,
    MAIL_SSL_TLS=get_settings().MAIL_SSL_TLS,
    USE_CREDENTIALS=get_settings().USE_CREDENTIALS,
    VALIDATE_CERTS=get_settings().VALIDATE_CERTS,
)

# テンプレート設定
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates_dir = BASE_DIR / "email_templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)

fm = FastMail(conf)


async def send_email(emails: list[str], template_name: str, subject: str, context: dict[str, Any]):
    """
    メールを送信する。

    Parameters
    ----------
    emails: list[str]
        送信先メールアドレスリスト
    template_name: str
        テンプレートファイル名
    subject: str
        メール件名
    context: dict[str, Any]
        メール本文コンテキスト
    """
    template = jinja_env.get_template(template_name)
    html = template.render(context)
    message = MessageSchema(
        subject=subject,
        recipients=emails,
        body=html,
        subtype=MessageType.html,
    )
    await fm.send_message(message)
