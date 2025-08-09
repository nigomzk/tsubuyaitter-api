import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Sequence, String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from app.core.config import get_settings
from app.core.database import Base
from app.enums import Flag


class BaseModelMixin:
    """
    基底モデル
    """

    @declared_attr
    def delete_flag(cls) -> Mapped[str]:
        return mapped_column(
            String(1), default=Flag.OFF.value, nullable=False, comment="削除フラグ"
        )

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


class User(Base, BaseModelMixin):
    """
    ユーザーモデル
    """

    __tablename__ = "users"
    user_id_seq = Sequence("user_id_seq")
    user_id: Mapped[str] = mapped_column(
        BigInteger,
        user_id_seq,
        primary_key=True,
        server_default=user_id_seq.next_value(),
        comment="ユーザーID",
    )
    username: Mapped[str] = mapped_column(String(15), index=True, unique=True, comment="ユーザー名")
    account_name: Mapped[str] = mapped_column(String(50), comment="アカウント名")
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, comment="メールアドレス"
    )
    birthday: Mapped[date] = mapped_column(Date, comment="生年月日")
    self_introduction: Mapped[str] = mapped_column(
        String(200), nullable=True, default=None, comment="自己紹介"
    )
    profile_image: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="プロフィール画像"
    )
    header_image: Mapped[str] = mapped_column(
        Text, nullable=True, default=None, comment="ヘッダー画像"
    )
    verified_flag: Mapped[str] = mapped_column(
        String(1), default=Flag.OFF.value, nullable=False, comment="認証済みフラグ"
    )
    auth_failure_count: Mapped[int] = mapped_column(Integer, default=0, comment="認証失敗回数")
    account_lock_flag: Mapped[str] = mapped_column(
        String(1), default=Flag.OFF.value, comment="アカウントロックフラグ"
    )

    refresh_tokens = relationship("UserRefreshToken", back_populates="user")


class UserCredential(Base, BaseModelMixin):
    """
    ユーザー認証情報モデル
    """

    __tablename__ = "user_credentials"
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), primary_key=True, comment="ユーザーID"
    )
    identity_type: Mapped[str] = mapped_column(String(20), primary_key=True, comment="識別子種別")
    identity: Mapped[str] = mapped_column(String(255), unique=True, comment="識別子")
    hashed_password: Mapped[str] = mapped_column(String(255), comment="ハッシュ化済みパスワード")

    user = relationship("User", back_populates="user_credentials")
