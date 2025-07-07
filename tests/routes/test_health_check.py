import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockFixture

from app.enums import HelthCheckStatus


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["is_connection_success", "expected_status_code", "expected_health_status", "expected_message"],
    [
        pytest.param(
            True, status.HTTP_200_OK, HelthCheckStatus.HEALTHY.value, "Success to connect server."
        ),
        pytest.param(
            False,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            HelthCheckStatus.UNHEALTHY.value,
            "Faild to get connection database.",
        ),
    ],
)
async def test_health_check(
    async_client: AsyncClient,
    mocker: MockFixture,
    is_connection_success: bool,
    expected_status_code: int,
    expected_health_status: str,
    expected_message: str,
):
    """
    ヘルスチェックAPIについて以下ケースを検証する

    +----+---+---+---+---+
    | No | DB接続成功 | HTTPステータスコード | ヘルスチェックステータス | メッセージ |
    +====+===+===+===+===+
    | 1 | o | 200 | Healthy | Success to connect server. |
    +----+---+---+---+---+
    | 2 | x | 503 | Unhealthy | Faild to get connection database. |
    +----+---+---+---+---+
    """
    if not is_connection_success:
        mocker.patch("app.crud.check_connection", side_effect=Exception("something exception"))
    response = await async_client.get("/health-check")
    assert response.status_code == expected_status_code

    response_obj = response.json()
    assert response_obj["status"] == expected_health_status
    assert response_obj["message"] == expected_message
