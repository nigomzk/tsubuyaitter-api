import re

import pytest
from pytest_mock import MockFixture
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.services import user_service


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["test_email", "expect_result"],
    [
        pytest.param("user0@sample.com", False),
        pytest.param("user1@sample.com", True),
    ],
)
async def test_is_registered_email(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
    test_email: str,
    expect_result: bool,
):
    """
    is_registered_emailについて以下ケースを検証する

    +--------------------------------------+------------------+---------------+
    | case                                 | email            | expect result |
    +======================================+==================+===============+
    | The email exists in database.        | user0@sample.com | False         |
    +--------------------------------------+------------------+---------------+
    | The email doesn't exist in database. | user1@sample.com | True          |
    +--------------------------------------+------------------+---------------+
    """
    async with get_test_session() as db:
        result = await user_service.is_registered_email(db, test_email)
        assert result == expect_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["test_username", "expect_result"],
    [
        pytest.param("user0", False),
        pytest.param("user1", True),
    ],
)
async def test_is_registered_username(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
    test_username: str,
    expect_result: bool,
):
    """
    is_registered_usernameについて以下ケースを検証する

    +-----------------------------------------+----------+---------------+
    | case                                    | username | expect result |
    +=========================================+==========+===============+
    | The username exists in database.        | user0    | False         |
    +-----------------------------------------+----------+---------------+
    | The username doesn't exist in database. | user1    | True          |
    +-----------------------------------------+----------+---------------+
    """
    async with get_test_session() as db:
        result = await user_service.is_registered_username(db, test_username)
        assert result == expect_result


@pytest.mark.asyncio
async def test_generate_initial_username(
    mocker: MockFixture,
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
):
    """"""
    # is_registered_usernameをmock化（呼び出し1度目は登録済み、2度目は未登録とする）
    mocked_func = mocker.patch(
        "app.services.user_service.is_registered_username", side_effect=[True, False]
    )
    expect_mocked_func_call_count = 2

    async with get_test_session() as db:
        # テスト対象関数呼び出し
        result = await user_service.generate_initial_username(db)
        assert mocked_func.call_count == expect_mocked_func_call_count
        assert (
            re.fullmatch(rf"([a-zA-Z0-9]{{{get_settings().USERNAME_MAX_LENGTH}}})", result)
            is not None
        )
