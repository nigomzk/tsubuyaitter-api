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


class ResposeHealthCheck(BaseModel):
    """
    ヘルスチェックレスポンス

    Attributes
    ----------
    status: HelthCheckStatus | str
        ステータス
    message: str
        メッセージ
    contents: list[HealthCheckItem]
        サーバ毎のヘルスチェック結果
    """

    status: HealthCheckStatus | str = HealthCheckStatus.HEALTHY
    message: str = "Success to connect servers."
    contents: list[HealthCheckItem] = []
