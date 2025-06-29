import pytest
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
