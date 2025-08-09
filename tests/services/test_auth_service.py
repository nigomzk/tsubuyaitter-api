import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Authcode
from app.services import auth_service


@pytest.mark.asyncio
async def test_send_authcode_by_email(
    get_test_session: async_sessionmaker[AsyncSession],
):
    """
    認証コードが発行・DB登録されること
    """
    # 実行前後の認証コード登録件数
    expect_before = 0
    expect_after = 1
    target_email = "test@sample.com"

    async with get_test_session() as db:
        # 実行前は登録件数0件
        result = (await db.scalars(select(Authcode))).all()
        assert len(result) == expect_before

        # テスト対象の関数実行
        authcode = await auth_service.send_authcode_by_email(db, target_email)

        # 実行後は登録件数1件
        result = (await db.scalars(select(Authcode))).all()
        assert len(result) == expect_after
        assert authcode.email == target_email


@freeze_time("2025-07-01 00:02:00")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["test_authcode_id", "test_code", "is_success"],
    [
        pytest.param("000000000002", "123452", True),
        pytest.param("000000000009", "123453", False),
        pytest.param("000000000003", "923453", False),
        pytest.param("000000000001", "123451", False),
    ],
)
async def test_verify_authcode(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_authcode: None,
    test_authcode_id: str,
    test_code: str,
    is_success: bool,
):
    """
    verify_authcodeについて以下ケースを検証する

    +----+------------------------------+--------------------------------------+--------+
    | No | case                         | authcode_id                          | code   |
    +====+==============================+======================================+========+
    | 1  | Success.                     | 00000000-0000-0000-0000-000000000002 | 123452 |
    +----+------------------------------+--------------------------------------+--------+
    | 2  | Error(authcode_id mismatch). | 00000000-0000-0000-0000-000000000009 | 123453 |
    +----+------------------------------+--------------------------------------+--------+
    | 3  | Error(code mismatch).        | 00000000-0000-0000-0000-000000000003 | 923453 |
    +----+------------------------------+--------------------------------------+--------+
    | 4  | Error(expired).              | 00000000-0000-0000-0000-000000000001 | 123451 |
    +----+------------------------------+--------------------------------------+--------+
    """
    test_authcode_id = f"00000000-0000-0000-0000-{test_authcode_id}"

    async with get_test_session() as db:
        if is_success:
            result = await auth_service.verify_authcode(db, test_authcode_id, test_code)
            assert result.authcode_id == test_authcode_id
            assert result.code == test_code
        else:
            with pytest.raises(HTTPException):
                await auth_service.verify_authcode(db, test_authcode_id, test_code)
