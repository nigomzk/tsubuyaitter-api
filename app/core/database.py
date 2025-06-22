import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import async_scoped_session, create_async_engine, AsyncSession, AsyncEngine
from urllib.parse import quote_plus
from app.core.config import get_settings

# 変数定義
dialect: str = get_settings().DATABASE_DIALECT
async_driver: str = get_settings().DATABASE_ASYNC_DRIVER
driver: str = get_settings().DATABASE_DRIVER
user: str = get_settings().DATABASE_USER
password: str = quote_plus(get_settings().DATABASE_PASSWORD)
host: str = get_settings().DATABASE_HOST
port: str = get_settings().DATABASE_PORT
db_name: str = get_settings().DATABASE_NAME
# DB接続先URL
DATABASE_URL = f"{dialect}+{async_driver}://{user}:{password}@{host}:{port}/{db_name}"
# マイグレーション用DB接続先URL
MIGRATION_URL = f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}" 
# DBオプション設定
DATABASE_OPTION = {
    "echo": get_settings().SQL_LOGGING,
    "echo_pool": get_settings().SQL_LOGGING,
    "pool_size": get_settings().DATABASE_POOL_SIZE,
    "pool_timeout": get_settings().POOL_CONN_TIMEOUT,
    "max_overflow": get_settings().DATABASE_MAX_OVERFLOW,
    "pool_recycle": get_settings().POOL_RECYCLE,
    "pool_pre_ping": True
  }

Base = declarative_base()

def async_session(engine: AsyncEngine) -> AsyncSession:
  async_session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=True,
  )
  # sessionのscope設定
  return async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)

async def get_session() -> AsyncSession:
  """
  DB sessionを取得する
  """
  async with async_session(
    create_async_engine(DATABASE_URL, **DATABASE_OPTION)
  ) as session:
    yield session