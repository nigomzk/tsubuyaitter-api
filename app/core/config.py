from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    環境変数を読み込む
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # 型チェック
    APP_ENV: str
    BASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_DIALECT: str
    DATABASE_ASYNC_DRIVER: str
    DATABASE_DRIVER: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int
    POOL_CONN_TIMEOUT: int
    POOL_RECYCLE: int
    SQL_LOGGING: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str
    TEST_DATABASE_NAME: str
    TEST_DATABASE_USER: str
    TEST_DATABASE_PASSWORD: str
    TEST_REDIS_DB: int
    AUTHCODE_LENGTH: int
    AUTHCODE_EXPIRE_MINUTES: int
    USERNAME_MAX_LENGTH: int
    PASSWORD_MAX_LENGTH: int
    PASSWORD_MIN_LENGTH: int


@lru_cache
def get_settings() -> Settings:
    """
    @lru_cacheで.envの結果をキャッシュする
    """
    return Settings.model_validate({})
