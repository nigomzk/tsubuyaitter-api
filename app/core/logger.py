import contextvars
import logging
from logging import Logger

from app.core.config import get_settings

request_id_contextvar = contextvars.ContextVar("request_id", default="default")


def _request_id() -> str:
    """
    contextVarsに保持したrequest_idを取得する。
    """
    return request_id_contextvar.get()


class AppLogger:
    """
    App用カスタムロガー
    """

    _logger_dict: dict[str, Logger] = {}

    def __init__(self, name: str):
        self.name = name

        logger = AppLogger._logger_dict.get(name)
        if isinstance(logger, Logger):
            self.logger = logger
        else:
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(get_settings().LOG_LEVEL)
            AppLogger._logger_dict[name] = self.logger

    def debug(self, msg: str, extra: dict[str, object] | None = None) -> None:
        self.logger.debug(f"[{_request_id()}] {msg}", extra=extra)

    def info(self, msg: str, extra: dict[str, object] | None = None) -> None:
        self.logger.info(f"[{_request_id()}] {msg}", extra=extra)

    def warning(self, msg: str, extra: dict[str, object] | None = None) -> None:
        self.logger.warning(f"[{_request_id()}] {msg}", extra=extra)

    def error(self, msg: str, extra: dict[str, object] | None = None) -> None:
        self.logger.error(f"[{_request_id()}] {msg}", extra=extra)

    def exception(self, msg: str) -> None:
        self.logger.exception(f"[{_request_id()}] {msg}")
