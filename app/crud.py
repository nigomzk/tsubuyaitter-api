from datetime import date

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Flag
from app.models import User, UserCredential
from app.schemas import user_schema


async def check_connection(db: AsyncSession) -> None:
    """
    DB接続を確認する。

    Parameters
    ----------
    db: AsyncSession
        DB接続session
    """
    await db.scalars(select(1))
    return


async def select_user_by_id(db: AsyncSession, user_id: int) -> user_schema.User | None:
    """
    ユーザーIDでユーザーを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DB接続
    user_id: int
        ユーザーID

    Returns
    -------
    User | None
        取得結果
    """
    result = (
        await db.scalars(
            select(User).where(and_(User.user_id == user_id, User.delete_flag == Flag.OFF.value))
        )
    ).first()
    return user_schema.User(**result.__dict__) if result else None


async def select_user_by_email(db: AsyncSession, email: str) -> user_schema.User | None:
    """
    メールアドレスでユーザーを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DB接続
    email: str
        メールアドレス

    Returns
    -------
    User | None
        取得結果
    """
    result = (
        await db.scalars(
            select(User).where(and_(User.email == email, User.delete_flag == Flag.OFF.value))
        )
    ).first()
    return user_schema.User(**result.__dict__) if result else None


async def select_user_by_username(db: AsyncSession, username: str) -> user_schema.User | None:
    """
    ユーザー名でユーザーを取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    username: str
        ユーザー名

    Returns
    -------
    User | None
        取得結果
    """
    result = (
        await db.scalars(
            select(User).where(and_(User.username == username, User.delete_flag == Flag.OFF.value))
        )
    ).first()
    return user_schema.User(**result.__dict__) if result else None


async def insert_user(
    db: AsyncSession, username: str, account_name: str, email: str, birthday: date
) -> user_schema.User:
    """
    ユーザーを登録する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    username: str
        ユーザー名
    account_name: str
        アカウント名（表示名）
    email: str
        メールアドレス
    birthday: datetime.date
        誕生日

    Returns
    -------
    app.schemas.user_schema.User:
        登録結果
    """
    user = User(username=username, account_name=account_name, email=email, birthday=birthday)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user_schema.User(**user.__dict__)


async def insert_user_credential(
    db: AsyncSession,
    user_id: int,
    identity_type: str,
    identity: str,
    hashed_password: str,
) -> user_schema.UserCredential:
    """
    ユーザー認証情報を登録する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    user_id: int
        ユーザーID
    identity_type: str
        識別子種別
    identity: str
        識別子
    hashed_password: str
        パスワード

    Returns
    -------
    app.schemas.user_schema.UserCredential:
        登録結果
    """
    user_credential = UserCredential(
        user_id=user_id,
        identity_type=identity_type,
        identity=identity,
        hashed_password=hashed_password,
    )
    db.add(user_credential)
    await db.commit()
    await db.refresh(user_credential)
    return user_schema.UserCredential(**user_credential.__dict__)


async def select_user_credential_by_identity(
    db: AsyncSession, identity: str
) -> user_schema.UserCredential | None:
    """
    ユーザー識別子でユーザー認証情報を取得する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    identity: str
        識別子
    Returns
    -------
    UserCredential | None
        取得結果
    """
    result = (
        await db.scalars(
            select(UserCredential).where(
                and_(
                    UserCredential.identity == identity,
                    UserCredential.delete_flag == Flag.OFF.value,
                )
            )
        )
    ).first()
    return user_schema.UserCredential(**result.__dict__) if result else None


async def select_user_credential_by_id_and_identity_type(
    db: AsyncSession, user_id: int, identity_type: str
) -> user_schema.UserCredential | None:
    """
    ユーザー認証情報をユーザーID、識別子種別で検索する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    user_id: int
        ユーザーID
    identity_type: str
        識別子種別

    Returns
    -------
    user_schema.UserCredential
        ユーザー認証情報
    """
    result = (
        await db.scalars(
            select(UserCredential).where(
                and_(
                    UserCredential.user_id == user_id,
                    UserCredential.identity_type == identity_type,
                    UserCredential.delete_flag == Flag.OFF.value,
                )
            )
        )
    ).first()
    return user_schema.UserCredential(**result.__dict__) if result else None


async def update_user_credential_hashed_password(
    db: AsyncSession, user_id: int, identity_type: str, hashed_password: str
) -> user_schema.UserCredential | None:
    """
    ユーザーID、識別子種別に一致するユーザー認証情報のハッシュ化済みパスワードを更新する。

    Parameters
    ----------
    db: sqlalchemy.ext.asyncio.AsyncSession
        DBセッション
    user_id: int
        ユーザーID
    identity_type: str
        識別子種別
    hashed_password: str
        ハッシュ化済みパスワード

    Returns
    -------
    list[user_schema.UserCredential]
        ユーザー認証情報リスト
    """
    result = (
        await db.scalars(
            update(UserCredential)
            .where(
                and_(
                    UserCredential.user_id == user_id,
                    UserCredential.identity_type == identity_type,
                    UserCredential.delete_flag == Flag.OFF.value,
                )
            )
            .values(hashed_password=hashed_password)
            .returning(UserCredential)
        )
    ).first()
    user_credential = user_schema.UserCredential(**result.__dict__) if result else None
    await db.commit()
    return user_credential
