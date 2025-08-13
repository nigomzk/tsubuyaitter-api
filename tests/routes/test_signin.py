from datetime import date

import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient
from jose import jwt
from pytest_mock import MockFixture

from app.core.config import get_settings
from app.schemas import token_schema, user_schema


@pytest.mark.asyncio
async def test_signin_for_authentication_successful(
    mocker: MockFixture,
    async_client: AsyncClient,
):
    """
    サインインAPIの正常系（認証成功）を検証する。
    """

    # リクエスト定義
    request_data = {
        "grant_type": "password",
        "username": "testuser",
        "password": "testpass",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    # モック定義
    mocked_user = user_schema.User(
        user_id=1,
        username="user",
        account_name="ユーザー",
        email="user@sample.com",
        birthday=date(2000, 1, 1),
        verified_flag="0",
        auth_failure_count=0,
        account_lock_flag="0",
    )
    mocker.patch("app.services.user_service.authenticate_user", return_value=mocked_user)

    # API実行
    response = await async_client.post("/signin", data=request_data)

    # HTTPステータスコードが 200 であること
    assert response.status_code == status.HTTP_200_OK

    # 返却された各トークン内のsub値が認証成功したユーザーのIDであること
    response_obj = response.json()
    decoded_access_token = jwt.decode(
        response_obj["access_token"],
        get_settings().SECRET_KEY,
        algorithms=[get_settings().ALGORITHM],
    )
    payload_access_token = token_schema.Payload(**decoded_access_token)
    assert payload_access_token.sub == str(mocked_user.user_id)

    decoded_refresh_token = jwt.decode(
        response_obj["refresh_token"],
        get_settings().SECRET_KEY,
        algorithms=[get_settings().ALGORITHM],
    )
    payload_refresh_token = token_schema.Payload(**decoded_refresh_token)
    assert payload_refresh_token.sub == str(mocked_user.user_id)


@pytest.mark.asyncio
async def test_signin_for_authentication_failed(
    mocker: MockFixture,
    async_client: AsyncClient,
):
    """
    サインインAPIの異常系（認証失敗）を検証する。
    """

    # リクエスト定義
    request_data = {
        "grant_type": "password",
        "username": "testuser",
        "password": "testpass",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    # モック定義
    mocker.patch(
        "app.services.user_service.authenticate_user",
        side_effect=HTTPException(status_code=status.HTTP_400_BAD_REQUEST),
    )

    # API実行
    response = await async_client.post("/signin", data=request_data)

    # HTTPステータスコードが 400 であること
    assert response.status_code == status.HTTP_400_BAD_REQUEST
