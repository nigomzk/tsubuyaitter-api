import pytest
from freezegun import freeze_time
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_issue_authcode_for_email(async_client: AsyncClient):
    """
    メール認証コード発行APIの正常系テスト

    Args:
        async_client (AsyncClient):
    """
    email = "test@sample.com"
    response = await async_client.post("/auth/email/issue-authcode", json={"email": email})
    response_obj = response.json()
    print("authcode_id: " + response_obj["authcode_id"])
    print("expire_datetime: " + response_obj["expire_datetime"])
    assert len(response_obj["authcode_id"]) == 36


@pytest.mark.parametrize(
    ["authcode_id", "code", "expect_status_code"],
    [
        pytest.param("00000000-0000-0000-0000-000000000099", "123451", 401),
        pytest.param("00000000-0000-0000-0000-000000000002", "923452", 401),
        pytest.param("00000000-0000-0000-0000-000000000003", "123453", 403),
        pytest.param("00000000-0000-0000-0000-000000000004", "123454", 200),
        pytest.param("00000000-0000-0000-0000-000000000099", "123455", 401),
        pytest.param("00000000-0000-0000-0000-000000000006", "923456", 401),
    ],
)
@freeze_time("2025-07-01 00:03:59")
@pytest.mark.asyncio
async def test_verify_authcode(
    async_client: AsyncClient,
    insert_test_data_authcode: None,
    authcode_id: str,
    code: str,
    expect_status_code: int,
):
    """
    認証コード検証APIについて以下ケースを検証する

    +----+---+---+---+---+
    | No | authcode_id一致 | 認証コード一致 | 有効期限内 | HTTPステータスコード(期待結果) |
    +====+===+===+===+===+
    | 1 | x | - | x | 401 |
    | 2 | o | x | x | 401 |
    | 3 | o | o | x | 403 |
    | 4 | o | o | o | 200 |
    | 5 | x | - | o | 401 |
    | 6 | o | x | o | 401 |
    +----+---+---+---+---+

    Parameters
    ----------
    async_client: httpx.AsyncClient
        テストクライアント
    insert_test_data_authcode: None
        認証コードテーブルテストデータ
    authcode_id: str
        認証コードID
    code: str
        認証コード
    expect_status_code: str
        HTTPステータスコード(期待結果)
    """
    response = await async_client.post(
        "/auth/verify-authcode", json={"authcode_id": authcode_id, "code": code}
    )
    assert response.status_code == expect_status_code
