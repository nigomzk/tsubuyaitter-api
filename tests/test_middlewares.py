import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.errors import ApiException
from app.middlewares import ErrorHandlingMiddleware


@pytest.mark.asyncio
async def test_ErrorHandlingMiddleware_when_apiException_occurs():
    """
    ApiException発生時に以下の形式でレスポンスが返却されること

    {
        "error": {
            "code": APIException.status_code,
            "message": "APIException.msg"
        }
    }
    """
    # テスト設定定義（発生させるエラー内容）
    test_status_code = status.HTTP_400_BAD_REQUEST
    test_error_messgae = "テストエラー"

    # 期待結果定義
    expected_status_code = test_status_code
    expected_message = test_error_messgae

    # テスト用アプリ定義
    test_app = FastAPI()
    test_app.add_middleware(ErrorHandlingMiddleware)

    # テスト用エンドポイント定義
    @test_app.get("/test")
    def test():  # pyright: ignore[reportUnusedFunction]
        raise ApiException(msg=test_error_messgae, status_code=test_status_code)

    # テスト用クライアント定義
    test_client = TestClient(test_app)

    # エンドポイント呼び出し
    response = test_client.get("/test")

    # 検証
    response_obj = response.json()
    assert response.status_code == expected_status_code
    assert response_obj["error"]["code"] == expected_status_code
    assert response_obj["error"]["message"] == expected_message


@pytest.mark.asyncio
async def test_ErrorHandlingMiddleware_when_unexpected_error_occurs():
    """
    想定外のエラー発生時に以下の形式でレスポンスが返却されること

    {
        "error": {
            "code": 500,
            "message": "システムエラーが発生しました。"
        }
    }
    """
    # テスト設定定義（発生させるエラー内容）
    test_error_messgae = "テストエラー"

    # 期待結果定義
    expected_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    expected_message = "システムエラーが発生しました。"

    # テスト用アプリ定義
    test_app = FastAPI()
    test_app.add_middleware(ErrorHandlingMiddleware)

    # テスト用エンドポイント定義
    @test_app.get("/test")
    def test():  # pyright: ignore[reportUnusedFunction]
        raise Exception(test_error_messgae)

    # テスト用クライアント定義
    test_client = TestClient(test_app)

    # エンドポイント呼び出し
    response = test_client.get("/test")

    # 検証
    response_obj = response.json()
    assert response.status_code == expected_status_code
    assert response_obj["error"]["code"] == expected_status_code
    assert response_obj["error"]["message"] == expected_message
