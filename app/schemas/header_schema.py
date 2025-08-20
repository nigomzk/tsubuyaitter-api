from uuid import UUID

from fastapi import Header
from pydantic import BaseModel


class CommonHeders(BaseModel):
    """
    共通ヘッダ
    """

    request_id: UUID = Header(...)
