import logging
import logging.handlers
from logging import FileHandler
from pathlib import Path

# the handler must live on module level, so that it is created only once
_rotating_file_handler: logging.handlers.RotatingFileHandler | None = None


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
    formatter = logging.Formatter(fmt="{asctime} {filename: <30} l. {lineno: >4} {levelname: <8} {message}", style="{")
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
    global _rotating_file_handler
    if not _rotating_file_handler:
        _rotating_file_handler = _make_handler(
            Path.home() / Path(".dsp-tools"),
            filesize_mb=100,
            backupcount=30,
        )
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(_rotating_file_handler)
    return logger


def get_log_filename_str(logger: logging.Logger) -> str:
    """
    This function returns a string, that lists the filenames of the loggers.

    Args:
        logger: logger

    Returns:
        Name(s) of the logger files
    """
    return ", ".join([handler.baseFilename for handler in logger.handlers if isinstance(handler, FileHandler)])
