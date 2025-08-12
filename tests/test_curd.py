from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import crud
from app.enums import Flag
from app.models import User


@pytest.mark.asyncio
async def test_check_connection(get_test_session: async_sessionmaker[AsyncSession]):
    """
    check_connectionのテストを行う
    """
    async with get_test_session() as db:
        result = await crud.check_connection(db)
        assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["email", "expected_hit", "expected_username"],
    [
        pytest.param("user1@sample.com", True, "user1"),
        pytest.param("user9@sample.com", False, None),
    ],
)
async def test_select_user_by_email(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
    email: str,
    expected_hit: bool,
    expected_username: str | None,
) -> None:
    """
    select_user_by_emailについて以下ケースを検証する。

    +----+-------------------------+---------------------------------+
    | No | expected hit in search. | expected username (case of hit) |
    +====+=========================+=================================+
    | 1  | True                    | user1                           |
    +----+-------------------------+---------------------------------+
    | 2  | False                   | -                               |
    +----+-------------------------+---------------------------------+
    """
    async with get_test_session() as db:
        result = await crud.select_user_by_email(db, email)
        if expected_hit:
            assert result is not None
            assert result.username == expected_username
        else:
            assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["username", "expected_hit", "expected_email"],
    [
        pytest.param("user1", True, "user1@sample.com"),
        pytest.param("user9", False, None),
    ],
)
async def test_select_user_by_username(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
    username: str,
    expected_hit: bool,
    expected_email: str | None,
) -> None:
    """
    select_user_by_usernameについて以下ケースを検証する。

    +----+-------------------------+------------------------------+
    | No | expected hit in search. | expected email (case of hit) |
    +====+=========================+==============================+
    | 1  | True                    | user1@sample.com             |
    +----+-------------------------+------------------------------+
    | 2  | False                   | -                            |
    +----+-------------------------+------------------------------+
    """
    async with get_test_session() as db:
        result = await crud.select_user_by_username(db, username)
        if expected_hit:
            assert result is not None
            assert result.email == expected_email
        else:
            assert result is None


@pytest.mark.asyncio
async def test_insert_user(get_test_session: async_sessionmaker[AsyncSession]) -> None:
    """
    insert_userでusersテーブルに1件レコードを登録できること。
    """

    username = "1234567890abcde"  # 15文字の文字列
    account_name = "テスト太郎"
    email = "test@sample.com"
    birthday = date(year=2000, month=12, day=24)
    expected_before = 0
    expected_after = 1
    async with get_test_session() as db:
        # 実行前は0件
        result = await db.scalars(select(User))
        assert len(result.all()) == expected_before

        # データ投入
        user = await crud.insert_user(db, username, account_name, email, birthday)
        assert user.username == username
        assert user.account_name == account_name
        assert user.email == email
        assert user.birthday == birthday
        assert user.account_lock_flag == Flag.OFF.value
        assert user.auth_failure_count == 0
        assert user.verified_flag == Flag.OFF.value

        # 実行後は1件
        result = await db.scalars(select(User))
        assert len(result.all()) == expected_after
