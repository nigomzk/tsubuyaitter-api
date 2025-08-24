from pydantic import BaseModel, Field

from app.enums import HealthCheckStatus
from app.schemas.health_check import HealthCheckItem


class HealthCheck(BaseModel):
    """
    ヘルスチェックレスポンススキーマ

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


class UserRegister(BaseModel):
    """
    ユーザー登録レスポンススキーマ
    """

    reception_id: str = Field(..., min_length=36, max_length=36, title="受付ID")
