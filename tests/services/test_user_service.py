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
