from pydantic import BaseModel

from app.enums import HelthCheckStatus


class ResposeHelthCheck(BaseModel):
    """
    ヘルスチェックレスポンス

    Attributes
    ----------
    status: HelthCheckStatus | str
        ステータス
    message: str
        メッセージ
    """

    status: HelthCheckStatus | str = HelthCheckStatus.HEALTHY
    message: str = "Success to connect server."
