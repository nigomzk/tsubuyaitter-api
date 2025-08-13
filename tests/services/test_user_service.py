import re

import pytest
import pytest_asyncio
from fastapi import HTTPException, status
from pytest_mock import MockFixture
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.models import UserCredential
from app.services import user_service


@pytest_asyncio.fixture(scope="function")
async def insert_undefined_user_credential(
    get_test_session: async_sessionmaker[AsyncSession],
) -> None:
    """
    未定義の識別子種別を投入する。
    """
    invalid_user_credential = UserCredential(
        user_id=3,
        identity_type="dummy",
        identity="user3",
        hashed_password="password3",
    )
    async with get_test_session() as db:
        db.add(invalid_user_credential)
        await db.commit()


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
    """
    generate_initial_username の検証を行う。
    """
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["test_identity", "test_password", "error_reason", "expected_user_id"],
    [
        pytest.param("user1", "password1", None, 1),
        pytest.param("user1@sample.com", "password1", None, 1),
        pytest.param("user1", "ng_password", "password_mismatch", None),
        pytest.param("user2", "password2", "no_user_credential", None),
        pytest.param("user3", "password3", "undefined_identity_type", None),
        # 外部キーの制約のため、実施不可のケース
        # pytest.param("user4", "password4", "no_user", None),
    ],
)
async def test_authenticate_user(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
    insert_undefined_user_credential: None,
    test_identity: str,
    test_password: str,
    error_reason: str | None,
    expected_user_id: int | None,
):
    """
    authenticate_user について以下ケースを検証する。

    +-------------------------------------------------------------+----------------------+
    | Case                                                        | Expected result      |
    +=============================================================+======================+
    | Authentication successful by username. (Normal case)        | Return User.         |
    +-------------------------------------------------------------+----------------------+
    | Authentication successful by email. (Normal case)           | Return User.         |
    +-------------------------------------------------------------+----------------------+
    | Password mismatch. (Abnormal case)                          | Raise HTTPException. |
    +-------------------------------------------------------------+----------------------+
    | User Credential doesn't exsits. (Abnormal case)             | Raise HTTPException. |
    +-------------------------------------------------------------+----------------------+
    | Authenticate by undifined user credential. (Abnormal case)  | Raise HTTPException. |
    +-------------------------------------------------------------+----------------------+
    """
    async with get_test_session() as db:
        if error_reason is None:
            result = await user_service.authenticate_user(
                db=db, identity=test_identity, password=test_password
            )
            assert result.user_id == expected_user_id
        else:
            with pytest.raises(HTTPException) as e:
                await user_service.authenticate_user(db, test_identity, test_password)

            assert isinstance(e.value, HTTPException)
            assert e.value.status_code == status.HTTP_400_BAD_REQUEST
            assert e.value.detail == "ユーザー名かパスワードが間違っています。"
