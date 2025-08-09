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
    expect_before = 0
    expect_after = 1
    async with get_test_session() as db:
        # 実行前は0件
        result = await db.scalars(select(Authcode))
        assert len(result.all()) == expect_before

        # 実行
        authcode = await crud.insert_authcode(db, email=email, code=code)
        assert authcode.code == code
        assert authcode.email == email

        # 実行後は1件
        result = await db.scalars(select(Authcode))
        assert len(result.all()) == expect_after


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
    expect_hit: bool,
    expect_username: str | None,
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
        if expect_hit:
            assert result is not None
            assert result.username == expect_username
        else:
            assert result is None
