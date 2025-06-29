from pathlib import Path

from app.core import config


def strtobool(val: str) -> bool:
    """
    True/Falseの文字列表現をBool型に変換する。

    'y', 'yes', 't', 'true', 'on', '1'： True

    'n', 'no', 'f', 'false', 'off', '0': False

    valが上記のいずれの値でもない場合は、ValueErrorをRaiseする。
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {val!r}")


def test_env_existing(root_dir_path: Path):
    """
    .envファイルの存在するかのテスト
    """
    env_path = root_dir_path / ".env"
    assert env_path.is_file()


def test_settings_env(root_dir_path: Path):
    """
    .envファイルの値取得のテスト
    """
    env_path = root_dir_path / ".env"
    with open(env_path, encoding="utf-8") as f:
        texts = f.readlines()

    env_values: dict[str, str] = {}
    for text in texts:
        if text == "\n" or text.startswith("#"):
            continue
        text = text.replace("\n", "")
        text = text.replace('"', "")
        key, value = text.split("=")[0], text.split("=")[1]
        env_values[key] = value

    # Compare with the values loaded in settings
    # アプリケーション設定
    assert env_values["APP_ENV"] == config.get_settings().APP_ENV
    assert env_values["BASE_URL"] == config.get_settings().BASE_URL

    # DB設定
    assert env_values["DATABASE_DIALECT"] == config.get_settings().DATABASE_DIALECT
    assert env_values["DATABASE_ASYNC_DRIVER"] == config.get_settings().DATABASE_ASYNC_DRIVER
    assert env_values["DATABASE_DRIVER"] == config.get_settings().DATABASE_DRIVER
    assert env_values["DATABASE_HOST"] == config.get_settings().DATABASE_HOST
    assert env_values["DATABASE_PORT"] == config.get_settings().DATABASE_PORT
    assert env_values["DATABASE_NAME"] == config.get_settings().DATABASE_NAME
    assert env_values["DATABASE_USER"] == config.get_settings().DATABASE_USER
    assert env_values["DATABASE_PASSWORD"] == config.get_settings().DATABASE_PASSWORD
    assert int(env_values["DATABASE_POOL_SIZE"]) == config.get_settings().DATABASE_POOL_SIZE
    assert int(env_values["DATABASE_MAX_OVERFLOW"]) == config.get_settings().DATABASE_MAX_OVERFLOW
    assert int(env_values["POOL_CONN_TIMEOUT"]) == config.get_settings().POOL_CONN_TIMEOUT
    assert int(env_values["POOL_RECYCLE"]) == config.get_settings().POOL_RECYCLE
    assert strtobool(env_values["SQL_LOGGING"]) == config.get_settings().SQL_LOGGING

    # 認証コード設定
    assert int(env_values["AUTHCODE_LENGTH"]) == config.get_settings().AUTHCODE_LENGTH
    assert (
        int(env_values["AUTHCODE_EXPIRE_MINUTES"]) == config.get_settings().AUTHCODE_EXPIRE_MINUTES
    )
