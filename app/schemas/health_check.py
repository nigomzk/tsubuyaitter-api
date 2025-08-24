from pydantic import BaseModel

from app.enums import HealthCheckStatus


class HealthCheckItem(BaseModel):
    """
    ヘルスチェック項目

    name: str
        項目名
    status: HelthCheckStatus | str
        ステータス
    message: str
        メッセージ
    """

    name: str
    status: HealthCheckStatus | str = HealthCheckStatus.HEALTHY
    message: str = "Success to connect server."
