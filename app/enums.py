from enum import Enum


class Flag(Enum):
    """
    フラグ

    OFF: 0
    ON: 1
    """

    OFF = "0"
    ON = "1"


class HealthcheckStatus(Enum):
    """
    ヘルスチェックステータス

    HEALTHY: Healthy
    UNHEALTHY: Unhealthy
    """

    HEALTHY = "Healthy"
    UNHEALTHY = "Unhealthy"


class IdentityType(Enum):
    """
    識別子種別

    USERNAME: username
    EMAIL: email
    """

    USERNAME = "username"
    EMAIL = "email"
