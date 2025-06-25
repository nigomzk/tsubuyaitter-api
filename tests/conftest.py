import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from urllib.parse import quote_plus
from app.core.config import get_settings
from app.core.database import DATABASE_OPTION, Base, get_session
from app.main import app

async def get_test_session():
  """
  テスト用のDB接続を取得する。
  """
  db_uri = (
    f"{get_settings().DATABASE_DIALECT}+{get_settings().DATABASE_ASYNC_DRIVER}://"
    f"{get_settings().TEST_DATABASE_USER}:{quote_plus(get_settings().TEST_DATABASE_PASSWORD)}@"
    f"{get_settings().DATABASE_HOST}:{get_settings().DATABASE_PORT}/{get_settings().TEST_DATABASE_NAME}"
  )
  engine: AsyncEngine = create_async_engine(db_uri, **DATABASE_OPTION)
  async_session: AsyncSession = async_sessionmaker(
    engine, 
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,
  )
  # SQLAlchemyで定義しているテーブルを全て作成する
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)

  async with async_session() as db:
    yield db

@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncClient:
  """
  テスト用の非同期HTTPクライアントを返却する。
  """
  # DIでFastAPIのDBの向き先をテスト用DBに変更
  app.dependency_overrides[get_session] = get_test_session

  # テスト用非同期HTTPクライアントを返却
  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    yield client
