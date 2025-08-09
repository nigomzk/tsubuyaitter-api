import pytest
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockFixture

from app.enums import HealthCheckStatus


@pytest.mark.asyncio
@pytest.mark.parametrize(
    [
        "is_db_connected",
        "is_redis_connected",
        "expected_http_status",
        "expected_db_health",
        "expected_redis_health",
        "expected_app_health",
    ],
    [
        pytest.param(
            True,
            True,
            status.HTTP_200_OK,
            HealthCheckStatus.HEALTHY.value,
            HealthCheckStatus.HEALTHY.value,
            HealthCheckStatus.HEALTHY.value,
        ),
        pytest.param(
            False,
            True,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            HealthCheckStatus.UNHEALTHY.value,
            HealthCheckStatus.HEALTHY.value,
            HealthCheckStatus.UNHEALTHY.value,
        ),
        pytest.param(
            True,
            False,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            HealthCheckStatus.HEALTHY.value,
            HealthCheckStatus.UNHEALTHY.value,
            HealthCheckStatus.UNHEALTHY.value,
        ),
        pytest.param(
            False,
            False,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            HealthCheckStatus.UNHEALTHY.value,
            HealthCheckStatus.UNHEALTHY.value,
            HealthCheckStatus.UNHEALTHY.value,
        ),
    ],
)
async def test_health_check(
    async_client: AsyncClient,
    mocker: MockFixture,
    is_db_connected: bool,
    is_redis_connected: bool,
    expected_http_status: int,
    expected_db_health: str,
    expected_redis_health: str,
    expected_app_health: str,
):
    """
    ヘルスチェックAPIについて以下ケースを検証する

    +----+----------+-------------+-------------+-----------+--------------+------------+
    | No | DB Conn. | Redis Conn. | HTTP Status | DB Health | Redis health | App health |
    +====+==========+=============+=============+===========+==============+============+
    | 1  | Sucess   | Sucess      | 200         | Healthy   | Healthy      | Healthy    |
    +----+----------+-------------+-------------+-----------+--------------+------------+
    | 2  | Fail     | Sucess      | 503         | Unhealthy | Healthy      | Unhealthy  |
    +----+----------+-------------+-------------+-----------+--------------+------------+
    | 3  | Sucess   | Fail        | 503         | Healthy   | UnHealthy    | Unhealthy  |
    +----+----------+-------------+-------------+-----------+--------------+------------+
    | 4  | Fail     | Fail        | 503         | UnHealthy | UnHealthy    | Unhealthy  |
    +----+----------+-------------+-------------+-----------+--------------+------------+
    """
    # 接続失敗するようにMock化
    if not is_db_connected:
        mocker.patch("app.crud.check_connection", side_effect=Exception("something exception"))
    if not is_redis_connected:
        mocker.patch(
            "app.core.redis.check_connection", side_effect=Exception("something exception")
        )
    response = await async_client.get("/health-check")
    assert response.status_code == expected_http_status

    # App全体のヘルスチェック結果
    response_obj = response.json()
    assert response_obj["status"] == expected_app_health

    healthcheck_list = response_obj["contents"]
    for item in healthcheck_list:
        # DBのヘルスチェック結果
        if item["name"] == "database":
            assert item["status"] == expected_db_health
        # Redisのヘルスチェック結果
        if item["name"] == "redis":
            assert item["status"] == expected_redis_health
