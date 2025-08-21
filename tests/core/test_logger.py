from logging import DEBUG, ERROR, INFO, WARNING

from _pytest.logging import LogCaptureFixture
from pytest_mock import MockFixture

from app.core.logger import AppLogger

test_request_id = "00000000-0000-0000-0000-000000000001"


def test_debug(mocker: MockFixture, caplog: LogCaptureFixture):
    """
    debugログ出力を検証する。
    """
    caplog.set_level(DEBUG)
    test_name = "app.test"
    test_msg = "test message."
    mocker.patch("app.core.logger._request_id", return_value=test_request_id)

    logger = AppLogger(test_name)
    logger.debug(test_msg)

    assert caplog.record_tuples == [(test_name, DEBUG, f"[{test_request_id}] {test_msg}")]


def test_info(mocker: MockFixture, caplog: LogCaptureFixture):
    """
    infoログ出力を検証する。
    """
    caplog.set_level(DEBUG)
    test_name = "app.test"
    test_msg = "test message."
    mocker.patch("app.core.logger._request_id", return_value=test_request_id)

    logger = AppLogger(test_name)
    logger.info(test_msg)

    assert caplog.record_tuples == [(test_name, INFO, f"[{test_request_id}] {test_msg}")]


def test_warning(mocker: MockFixture, caplog: LogCaptureFixture):
    """
    warningログ出力を検証する。
    """
    caplog.set_level(DEBUG)
    test_name = "app.test"
    test_msg = "test message."
    mocker.patch("app.core.logger._request_id", return_value=test_request_id)

    logger = AppLogger(test_name)
    logger.warning(test_msg)

    assert caplog.record_tuples == [(test_name, WARNING, f"[{test_request_id}] {test_msg}")]


def test_error(mocker: MockFixture, caplog: LogCaptureFixture):
    """
    warningログ出力を検証する。
    """
    caplog.set_level(DEBUG)
    test_name = "app.test"
    test_msg = "test message."
    mocker.patch("app.core.logger._request_id", return_value=test_request_id)

    logger = AppLogger(test_name)
    logger.error(test_msg)

    assert caplog.record_tuples == [(test_name, ERROR, f"[{test_request_id}] {test_msg}")]


def test_exception(mocker: MockFixture, caplog: LogCaptureFixture):
    """
    exceptionログ出力を検証する。
    """
    caplog.set_level(DEBUG)
    test_name = "app.test"
    test_msg = "test message."
    mocker.patch("app.core.logger._request_id", return_value=test_request_id)

    logger = AppLogger(test_name)
    try:
        raise ValueError()
    except ValueError:
        logger.exception(test_msg)

    assert caplog.record_tuples == [(test_name, ERROR, f"[{test_request_id}] {test_msg}")]
