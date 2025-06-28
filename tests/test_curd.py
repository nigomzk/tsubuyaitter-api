import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import crud
from app.models import Authcode

@pytest.mark.asyncio
async def test_insert_authcode(get_test_session: async_sessionmaker[AsyncSession]):
  """
  以下観点でinsert_authcodeのテストを行う

  観点
  ----
  ・authcodesテーブルに1件登録できること
  """
  email = "test@sample.com"
  code = "123456"
  expect_before = 0
  expect_after = 1
  async with get_test_session() as db:
    # 実行前は0件
    result = await db.scalars(select(Authcode))
    assert len(result.all()) == expect_before

    # 実行
    authcode: Authcode = await crud.insert_authcode(db, email=email, code=code)
    assert str(authcode.code) == code
    assert str(authcode.email) == email

    # 実行後は1件
    result = await db.scalars(select(Authcode))
    assert len(result.all()) == expect_after