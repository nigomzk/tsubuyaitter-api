from pydantic import BaseModel

from app.enums import HealthcheckStatus


class HealthcheckItem(BaseModel):
    """
    ヘルスチェック項目

    name: str
        項目名
    status: HelthcheckStatus | str
        ステータス
    message: str
        メッセージ
    """

    name: str
    status: HealthcheckStatus | str = HealthcheckStatus.HEALTHY
    message: str = "Success to connect server."
