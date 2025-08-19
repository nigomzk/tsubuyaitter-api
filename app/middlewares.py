import logging
import time
from collections.abc import Awaitable, Callable
from logging import Logger

from fastapi import Request, Response
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

logger: Logger = logging.getLogger(f"{__name__}")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    リクエスト・レスポンスのログ記録を行うミドルウェア
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        リクエスト・レスポンスのログ記録を行う
        """
        start_time = time.time()
        req_data = {}

        # リクエストボディを読み取る（BodyがNoneの場合エラーとなるため値有のときのみ読み取る）
        if request.method == "POST" and not await request.body():
            req_data["Body"] = await request.json()
        logger.info(f"Request : {request.method} {request.url} {req_data}")

        response = await call_next(request)

        # レスポンスボディを読み取る
        res_body = [section async for section in response.body_iterator]  # type:ignore
        response.body_iterator = iterate_in_threadpool(iter(res_body))  # type:ignore
        res_body = res_body[0].decode()  # type:ignore
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code}, {process_time:.4f} sec, {res_body}")
        return response
