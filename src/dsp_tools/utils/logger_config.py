import sys
from pathlib import Path

from loguru import logger


def logger_config() -> None:
    """
    This function configures the log files.
    Currently, there are three sinks:
    - logger.log in the home directory for development purposes
    - warnings.log in the cwd only with level warning and higher for the user (no stack-trace)
    - print output on the terminal, formatted the same as the warnings.log

    Returns:
        None
    """
    # If this is not removed, the default formatting is also printed out on the terminal
    logger.remove()

    text_format = "{time:YYYY-MM:DD HH:mm:ss.SSSS} | <level>{level} | {message}</level>"
    rotation_size = "104857600 MB"
    retention_number = 30

    logger.add(sink=sys.stdout, format=text_format, level="INFO", backtrace=False, diagnose=False)

    logger.add(
        sink=Path.home() / Path(".dsp-tools") / Path("loguru.log"),
        format=text_format,
        serialize=True,
        backtrace=True,
        diagnose=True,
        rotation=rotation_size,
        retention=retention_number,
    )

    logger.add(
        sink=Path("warnings.log"),
        level="WARNING",
        format=text_format,
        rotation=rotation_size,
        retention=10,
    )
