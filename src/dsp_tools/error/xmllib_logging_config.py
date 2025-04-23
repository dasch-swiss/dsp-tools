import sys

from loguru import logger


def configure_logging() -> None:
    logger.remove()

    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level} | Function: '{function}' | {message}</level>",
        colorize=True,
    )
