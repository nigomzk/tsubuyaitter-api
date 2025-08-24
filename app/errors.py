import traceback

from fastapi import status


class ApiException(Exception):
    """
    業務例外
    """

    default_statuse_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        msg: str,
        status_code: int = default_statuse_code,
    ) -> None:
        self.status_code = status_code
        self.detail: dict[str, dict[str, int | str]] = {
            "error": {"code": status_code, "message": msg}
        }


class SystemException(Exception):
    """
    システム例外
    """

    def __init__(self, e: Exception) -> None:
        self.exc = e
        self.stack_trace = traceback.format_exc()
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail: dict[str, dict[str, int | str]] = {
            "error": {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "システムエラーが発生しました。",
            }
        }
