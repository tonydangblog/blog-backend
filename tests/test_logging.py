"""Test Logging Module."""
# pylint: disable=missing-class-docstring,too-few-public-methods,no-self-use
# pylint: disable=missing-function-docstring,unused-argument,too-many-arguments

from pathlib import Path
from typing import Generator

from flask import url_for
from freezegun import freeze_time
from pytest import fixture
from werkzeug.test import Client

from app.logging import create_logger


@fixture
def test_log() -> Generator[Path, None, None]:
    # SETUP Create test.log file path. Remove file and parent directory if present.
    log_file = Path(__file__).parents[1] / "logs" / "test" / "test.log"
    log_file.unlink(missing_ok=True)
    if log_file.parent.is_dir():
        log_file.parent.rmdir()
    assert (log_file.is_file(), log_file.parent.is_dir()) == (False, False)  # nosec
    # TEST
    yield log_file
    # TEARDOWN Remove test.log file and parent directory.
    log_file.unlink(missing_ok=False)
    log_file.parent.rmdir()


def test_creates_log_file(test_log: Path) -> None:
    # GIVEN No test.log file in logs/test directory.
    # WHEN Logger with name "test" is created.
    create_logger("test")
    # THEN Test.log file is present in logs/test directory.
    assert test_log.is_file()  # nosec


@freeze_time("2021-01-01")
def test_logs_record_without_request_context(test_log: Path) -> None:
    # GIVEN No test.log file in logs/test directory.
    # WHEN Logger with name "test" is created and record without request context is
    #      logged.
    test_logger = create_logger("test")
    test_logger.info("msg")
    log_msg = (
        "[2021-01-01 00:00:00,000 UTC] INFO in test_logging -\n"
        "IP: None\n"
        "Method: None\n"
        "URL: None\n"
        "User Agent: None\n"
        "File: "
        '"/Users/tonydang/Dropbox/root/blog/backend/tests/test_logging.py", line 45\n'
        "Message: msg\n\n"
    )
    # THEN Record without request context is logged in proper format.
    assert test_log.read_text() == log_msg  # nosec


@freeze_time("2021-01-01")
def test_logs_record_with_request_context(test_log: Path, client: Client) -> None:
    # GIVEN No test.log file in logs/test directory.
    # WHEN Logger with name "test" is created and record with request context is logged.
    test_logger = create_logger("test")
    client.get(url_for("main.home"))
    test_logger.info("msg")
    log_msg1 = (
        "[2021-01-01 00:00:00,000 UTC] INFO in test_logging -\n"
        "IP: 127.0.0.1\n"
        "Method: GET\n"
        "URL: http://localhost/\n"
        "User Agent: werkzeug/"
    )
    log_msg2 = (
        "File: "
        '"/Users/tonydang/Dropbox/root/blog/backend/tests/test_logging.py", line 66\n'
        "Message: msg\n\n"
    )
    # THEN Record with request context is logged in proper format.
    log_msg = test_log.read_text()
    assert (log_msg1 in log_msg, log_msg2 in log_msg) == (True, True)  # nosec
