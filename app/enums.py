from enum import Enum


class Flag(Enum):
    """
    フラグ

    OFF: 0
    ON: 1
    """

    OFF = "0"
    ON = "1"


class HealthCheckStatus(Enum):
    """
    ヘルスチェックステータス

    HEALTHY: Healthy
    UNHEALTHY: Unhealthy
    """

    HEALTHY = "Healthy"
    UNHEALTHY = "Unhealthy"
