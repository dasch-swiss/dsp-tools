import logging
import logging.handlers
from pathlib import Path
from typing import cast

rotating_file_handler: logging.handlers.RotatingFileHandler | None = None


def _make_handler(
    logfile_directory: Path = Path.home() / Path(".dsp-tools"),
    filesize_mb: int = 20,
    backupcount: int = 10,
) -> None:
    """
    Create a formatter and a rotating file handler.
    They must live on module level, so that they are created only once.

    A RotatingFileHandler fills "filename" until it is "maxBytes" big,
    then appends ".1" to it and starts with a new file "filename",
    fills it until it is "maxBytes" big,
    then appends ".1" to it (replacing the old ".1" file)
    """
    formatter = logging.Formatter(fmt="{asctime} {filename: <20} {levelname: <8} {message}", style="{")
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

    global rotating_file_handler
    rotating_file_handler = handler


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
    global rotating_file_handler
    if not rotating_file_handler:
        _make_handler()
        rotating_file_handler = cast(logging.handlers.RotatingFileHandler, rotating_file_handler)
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.addHandler(rotating_file_handler)
    return _logger
