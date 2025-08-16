import re

import pytest
import pytest_asyncio
from fastapi import HTTPException, status
from pydantic import SecretStr
from pytest_mock import MockFixture
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.enums import IdentityType
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
    ["user_id", "identity_types", "is_error", "expected_insert_count", "expected_update_count"],
    [
        pytest.param(9, [IdentityType.USERNAME], True, 0, 0),
        pytest.param(2, [IdentityType.USERNAME], False, 1, 0),
        pytest.param(1, [IdentityType.USERNAME], False, 0, 1),
        pytest.param(1, [IdentityType.EMAIL], False, 0, 1),
        pytest.param(1, [IdentityType.EMAIL, IdentityType.USERNAME], False, 0, 2),
    ],
)
async def test_set_password(
    get_test_session: async_sessionmaker[AsyncSession],
    insert_test_data_user: None,
    mocker: MockFixture,
    user_id: int,
    identity_types: list[IdentityType],
    is_error: bool,
    expected_insert_count: int,
    expected_update_count: int,
):
    """
    set_passwordについて以下ケースの検証を行う。

    +--------------------------------------------------------------------+-------------------------+
    | No | Case                                                          | Expected result         |
    +====+===============================================================+=========================+
    | 1  | Set user_id that doesn't exist in user_credentials.           | Raise HTTPException.    |
    +--------------------------------------------------------------------+-------------------------+
    | 2  | Set an unexpected identity_type.                              | Raise HTTPException.    |
    +--------------------------------------------------------------------+-------------------------+
    | 3  | Set identity_type (email) that exists in user_credentials.    | Update user_credential. |
    +--------------------------------------------------------------------+-------------------------+
    | 4  | Set identity_type (username) that exists in user_credentials. | Update user_credential. |
    +--------------------------------------------------------------------+-------------------------+
    | 5  | Set multiple identity_type that exists in user_credentials.   | Update user_credentials.|
    +--------------------------------------------------------------------+-------------------------+
    """
    test_password = "updeted_password"

    # mock化
    mocker.patch("app.core.security.get_password_hash", return_value=test_password)
    mock_insert_func = mocker.patch("app.crud.insert_user_credential", return_value=None)
    mock_update_func = mocker.patch(
        "app.crud.update_user_credential_hashed_password", return_value=None
    )

    async with get_test_session() as db:
        if is_error:
            # 対象の関数を実行
            with pytest.raises(HTTPException) as e:
                await user_service.set_password(
                    db,
                    user_id=user_id,
                    identity_types=identity_types,
                    password=SecretStr(test_password),
                )
                assert isinstance(e.value, HTTPException)
                assert e.value.status_code == status.HTTP_400_BAD_REQUEST
                assert e.value.detail == "不正なリクエストです。"
        else:
            # 対象の関数を実行
            await user_service.set_password(
                db,
                user_id=user_id,
                identity_types=identity_types,
                password=SecretStr(test_password),
            )
            assert mock_insert_func.call_count == expected_insert_count
            assert mock_update_func.call_count == expected_update_count


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
