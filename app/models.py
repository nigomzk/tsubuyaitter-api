import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, String

from app.core.config import get_settings
from app.core.database import Base


class CommonColumns:
    """
    共通カラム
    """

    delete_flag = Column(Boolean, default=False, nullable=False, comment="削除フラグ")
    create_datetime = Column(DateTime, default=datetime.now(), nullable=False, comment="作成日時")
    update_datetime = Column(
        DateTime,
        default=datetime.now(),
        onupdate=datetime.now(),
        nullable=False,
        comment="更新日時",
    )


class Authcode(Base, CommonColumns):
    """
    認証コード
    """

    __tablename__ = "authcodes"
    authcode_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="認証コードID",
    )
    code = Column(String(6), nullable=False, comment="コード")
    email = Column(String(255), nullable=False, comment="メールアドレス")
    expire_datetime = Column(
        DateTime,
        default=(datetime.now() + timedelta(minutes=get_settings().AUTHCODE_EXPIRE_MINUTES)),
        nullable=False,
        comment="有効期限",
    )
