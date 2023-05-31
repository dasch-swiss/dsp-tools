import logging
import logging.handlers
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Create a logger instance, 
    set its level to INFO,
    and configure it to write to a file in the user's home directory.
    
    Args:
        name: name of the logger

    Returns:
        the logger instance
    """
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="{asctime} {filename: <20} {levelname: <8} {message}",
        style="{"
    )
    # a RotatingFileHandler fills "filename" until it is "maxBytes" big, 
    # then appends ".1" to it and starts with a new file "filename",
    # fills it until it is "maxBytes" big,
    # then appends ".1" to it (replacing the old ".1" file)
    logfile_directory = Path.home() / Path(".dsp-tools")
    logfile_directory.mkdir(exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        filename=logfile_directory / "logging.log",
        mode="a",
        maxBytes=3*1024*1024,
        backupCount=1
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger
