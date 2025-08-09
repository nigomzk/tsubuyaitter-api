from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import crud
from app.enums import Flag
from app.models import Authcode, User


@pytest.mark.asyncio
async def test_check_connection(get_test_session: async_sessionmaker[AsyncSession]):
    """
    check_connectionのテストを行う
    """
    async with get_test_session() as db:
        result = await crud.check_connection(db)
        assert result is None


@pytest.mark.asyncio
async def test_insert_authcode(get_test_session: async_sessionmaker[AsyncSession]):
    """
    以下観点でinsert_authcodeのテストを行う

    観点
    ----
    ・authcodesテーブルに1件登録できること
    """
    email = "test@sample.com"
    code = "123456"
    expected_before = 0
    expected_after = 1
    async with get_test_session() as db:
        # 実行前は0件
        result = await db.scalars(select(Authcode))
        assert len(result.all()) == expected_before

        # 実行
        authcode = await crud.insert_authcode(db, email=email, code=code)
        assert authcode.code == code
        assert authcode.email == email

        # 実行後は1件
        result = await db.scalars(select(Authcode))
        assert len(result.all()) == expected_after


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["authcode_id", "expected_hit", "expected_code", "expected_expire_datetime"],
    [
        pytest.param(
            "00000000-0000-0000-0000-000000000001", True, "123451", "2025-07-01 00:01:00.999999"
        ),
        pytest.param("00000000-0000-0000-0000-000000000099", False, None, None),
    ],
)
async def test_select_authcode_by_id(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_authcode: None,
    authcode_id: str,
    expected_hit: bool,
    expected_code: str | None,
    expected_expire_datetime: str | None,
) -> None:
    """
    select_authcode_by_idについて以下ケースを検証する

    +----+---+---+
    | No | authcode_id一致 | 取得件数(期待結果) |
    +====+===+===+
    | 1 | o | 1 |
    +----+---+---+
    | 2 | x | 0 |
    +----+---+---+

    Parameters
    ----------
    get_test_session: sqlalchemy.ext.asyncio.async_sessionmaker[AsyncSession]
        テスト用DBセッション
    insert_test_data_authcod: None
        テストデータ投入処理
    authcode_id: str
        認証コードID
    expected_hit: bool
        データの存在有無
    expected_code: str | None
        認証コード
    expected_expire_datetime: str | None
        有効期限日時
    """

    async with get_test_session() as db:
        result = await crud.select_authcode_by_id(db, authcode_id=authcode_id)
        if expected_hit:
            assert result is not None
            assert result.code == expected_code
            assert str(result.expire_datetime) == expected_expire_datetime
        else:
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
