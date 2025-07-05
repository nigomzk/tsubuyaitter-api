from datetime import datetime

from pydantic import BaseModel, Field


class BaseSechemaMixin(BaseModel):
    """
    基底スキーマ

    Attributes
    ----------
    delete_flag: str
        削除フラグ
    create_datetime: datetime.datetime
        作成日時
    update_datetime: datetime.datetime
        更新日時
    """

    delete_flag: str | None = Field(..., title="削除フラグ")
    create_datetime: datetime | None = Field(..., title="作成日時")
    update_datetime: datetime | None = Field(..., title="更新日時")
