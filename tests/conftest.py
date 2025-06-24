import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from urllib.parse import quote_plus
from app.core.config import get_settings
from app.core.database import DATABASE_OPTION, Base, get_session
from app.main import app

dialect: str = get_settings().DATABASE_DIALECT
async_driver: str = get_settings().DATABASE_ASYNC_DRIVER
user = get_settings().TEST_DATABASE_USER
password: str = quote_plus(get_settings().TEST_DATABASE_PASSWORD)
host: str = get_settings().DATABASE_HOST
port: str = get_settings().DATABASE_PORT
db_name: str = get_settings().TEST_DATABASE_NAME
DATABASE_URL = f"{dialect}+{async_driver}://{user}:{password}@{host}:{port}/{db_name}"

@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
  engine: AsyncEngine = create_async_engine(DATABASE_URL, **DATABASE_OPTION)
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

  # DIでFastAPIのDBの向き先をテスト用DBに変更
  async def get_test_session():
    async with async_session() as db:
      yield db

  app.dependency_overrides[get_session] = get_test_session

  # テスト用非同期HTTPクライアントを返却
  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    yield client
