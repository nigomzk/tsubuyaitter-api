import uuid
from datetime import datetime, timedelta

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.core.config import get_settings
from app.core.database import Base


class BaseModelMixin:
    """
    基底モデル
    """

    @declared_attr
    def delete_flag(cls) -> Mapped[bool]:
        return mapped_column(Boolean, default=False, nullable=False, comment="削除フラグ")

    @declared_attr
    def create_datetime(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, default=datetime.now(), nullable=False, comment="作成日時")

    @declared_attr
    def update_datetime(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime,
            default=datetime.now(),
            onupdate=datetime.now(),
            nullable=False,
            comment="更新日時",
        )


class Authcode(Base, BaseModelMixin):
    """
    認証コードモデル
    """

    __tablename__ = "authcodes"
    authcode_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="認証コードID",
    )
    code: Mapped[str] = mapped_column(String(6), nullable=False, comment="コード")
    email: Mapped[str] = mapped_column(String(255), nullable=False, comment="メールアドレス")
    expire_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        default=(datetime.now() + timedelta(minutes=get_settings().AUTHCODE_EXPIRE_MINUTES)),
        nullable=False,
        comment="有効期限",
    )
