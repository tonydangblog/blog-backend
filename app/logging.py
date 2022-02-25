"""Logging Module.

Helper functions for creating loggers with rotating file handlers. Logs are stored
under 'logs' directory in project root.
"""

from logging import Formatter, Logger, LogRecord, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from time import gmtime

from flask import has_request_context, request


class RequestFormatter(Formatter):
    """Formatter subclass with additional flask request info."""

    converter = gmtime  # Convert timestamp to UTC.

    def format(self, record: LogRecord) -> str:
        """Add request IP, method, and URL to record attributes for formatting."""
        if has_request_context():
            setattr(record, "remote_addr", request.remote_addr)
            setattr(record, "method", request.method)
            setattr(record, "url", request.url)
            setattr(record, "user_agent", request.user_agent)
        else:
            attributes = ("remote_addr", "method", "url", "user_agent")
            for attribute in attributes:
                setattr(record, attribute, None)
        return super().format(record)


def create_file_handler(logger_name: str) -> RotatingFileHandler:
    """Create rotating file handler for logger."""
    log_dir = Path(__file__).parents[1] / "logs" / logger_name
    if not log_dir.is_dir():
        log_dir.mkdir()
    handler = RotatingFileHandler(
        filename=log_dir / f"{logger_name}.log",
        maxBytes=1024 ** 2,
        backupCount=10,
    )
    formatter = RequestFormatter(
        "[{asctime} UTC] {levelname} in {module} -\n"
        "IP: {remote_addr}\n"
        "Method: {method}\n"
        "URL: {url}\n"
        "User Agent: {user_agent}\n"
        'File: "{pathname}", line {lineno}\n'
        "Message: {message}\n",
        style="{",
    )
    handler.setFormatter(formatter)
    handler.setLevel("INFO")
    return handler


def create_logger(logger_name: str) -> Logger:
    """Create logger."""
    logger = getLogger(logger_name)
    logger.addHandler(create_file_handler(logger_name))
    logger.setLevel("INFO")
    return logger
