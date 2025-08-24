from pydantic import BaseModel, Field

from app.enums import HealthcheckStatus
from app.schemas.healthcheck_schema import HealthcheckItem


class Healthcheck(BaseModel):
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

    status: HealthcheckStatus | str = HealthcheckStatus.HEALTHY
    message: str = "Success to connect servers."
    contents: list[HealthcheckItem] = []


class UserRegister(BaseModel):
    """
    ユーザー登録レスポンススキーマ
    """

    reception_id: str = Field(..., min_length=36, max_length=36, title="受付ID")
