import contextvars
import json
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import AppLogger, request_id_contextvar

logger: AppLogger = AppLogger(f"{__name__}")


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

        # ログにリクエストIDを設定するため、ContextVarsに値を保持
        headers = request.headers
        request_id = headers.get("request-id")
        request_id_contextvar.set(str(request_id))
        ctx = contextvars.copy_context()

        # リクエストボディを読み取る（BodyがNoneの場合エラーとなるため値有のときのみ読み取る）
        if request.method == "POST" and not await request.body():
            req_data["Body"] = await request.json()
        logger.info(f"処理を開始します。[URL = {request.url}, Request = {req_data}]")

        response = await ctx.run(call_next, request)

        # レスポンスボディを読み取る
        res_body = [section async for section in response.body_iterator]  # type:ignore
        response.body_iterator = iterate_in_threadpool(iter(res_body))  # type:ignore
        res_body = res_body[0].decode()  # type:ignore
        try:
            # json形式でデコード
            res_body = json.loads(res_body)  # type:ignore
            # セキュアな情報のログ出力抑止
            secret_keys = ["access_token", "refresh_token"]
            for secret_key in secret_keys:
                if res_body and (secret_key in res_body):
                    res_body[secret_key] = "********"
        except json.JSONDecodeError:
            # json形式でデコードできない場合は何もしない
            pass
        process_time = time.time() - start_time
        logger.info(f"処理を終了します。[URL = {request.url}, Response = {res_body}]")
        logger.info(
            f"URL={request.url}, http_status={response.status_code}, "
            f"response_time={process_time:.4f}"
        )
        return response
