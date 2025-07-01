import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import crud
from app.models import Authcode


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
        authcode: Authcode = await crud.insert_authcode(db, email=email, code=code)
        assert str(authcode.code) == code
        assert str(authcode.email) == email

        # 実行後は1件
        result = await db.scalars(select(Authcode))
        assert len(result.all()) == expect_after


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["authcode_id", "expected_hit", "expected_code", "expected_expire_datetime"],
    [
        pytest.param(
            "00000000-0000-0000-0000-000000000001", True, "123451", "2025-07-01 23:59:59.991000"
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
    以下観点でselect_authcode_by_idのテストを行う

    ・authcode_idに一致するデータが存在する場合、1件データを取得できること

    ・authcode_idに一致するデータが存在しない場合、データを取得できないこと

    Args:
        get_test_session (async_sessionmaker[AsyncSession]): テスト用DBセッション
        insert_test_data_authcode (None): テストデータ投入処理
        authcode_id (str): 認証コードID
        expected_hit (bool): データの存在有無
        expected_code (str | None): コード値
        expected_expire_datetime (str | None): 有効期限日時
    """
    async with get_test_session() as db:
        result = await crud.select_authcode_by_id(db, authcode_id)
        if expected_hit:
            assert result is not None
            assert str(result.code) == expected_code
            assert str(result.expire_datetime) == expected_expire_datetime
        else:
            assert result is None
