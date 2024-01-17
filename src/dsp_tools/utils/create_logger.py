import http.client
import logging
import logging.handlers
from pathlib import Path
from typing import Any

# these must live on module level, so that they are created only once
_rotating_file_handler: logging.handlers.RotatingFileHandler | None = None
_requests_logger: logging.Logger | None = None
_http_client_logger: logging.Logger | None = None


def _make_handler(
    logfile_directory: Path,
    filesize_mb: int,
    backupcount: int,
) -> logging.handlers.RotatingFileHandler:
    """
    Create a rotating file handler.
    A RotatingFileHandler fills "filename" until it is "maxBytes" big,
    then appends ".1" to it and starts with a new file "filename",
    fills it until it is "maxBytes" big,
    then appends ".1" to it (replacing the old ".1" file)

    Args:
        logfile_directory: directory to store the logfiles in
        filesize_mb: maximum size of a logfile in MB
        backupcount: number of logfiles to keep

    Returns:
        handler instance
    """
    formatter = logging.Formatter(fmt="{asctime} {filename: <30} {levelname: <8} {message}", style="{")
    formatter.default_time_format = "%Y-%m-%d %H:%M:%S"
    formatter.default_msec_format = "%s.%03d"

    logfile_directory.mkdir(exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        filename=logfile_directory / "logging.log",
        mode="a",
        maxBytes=filesize_mb * 1024 * 1024,
        backupCount=backupcount,
    )
    handler.setFormatter(formatter)
    return handler


def _make_requests_logger() -> None:
    global _requests_logger
    if not _requests_logger:
        http.client.HTTPConnection.debuglevel = 1
        _requests_logger = logging.getLogger("requests.packages.urllib3")
        _requests_logger.setLevel(logging.DEBUG)
        _requests_logger.propagate = True


def _make_http_client_logger() -> None:
    """
    monkey-patch a `print` global into the http.client module.
    all calls to print() in that module will then use our print_to_log implementation
    """
    global _http_client_logger
    if not _http_client_logger:
        _http_client_logger = logging.getLogger("http.client")
        _http_client_logger.setLevel(logging.DEBUG)

        def print_to_log(*args: Any) -> None:
            if not args[0].startswith("header"):
                _http_client_logger.debug(" ".join(args))

        http.client.print = print_to_log  # type: ignore[attr-defined]


def get_logger(
    name: str,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Create a logger instance,
    and configure it to write to a file in the user's home directory.

    Args:
        name: name of the logger
        level: logging level, defaults to logging.DEBUG

    Returns:
        the logger instance
    """
    _make_requests_logger()
    _make_http_client_logger()
    global _rotating_file_handler
    if not _rotating_file_handler:
        _rotating_file_handler = _make_handler(
            Path.home() / Path(".dsp-tools"),
            filesize_mb=100,
            backupcount=30,
        )
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logging.getLogger().addHandler(_rotating_file_handler)
    return logger
