import sys

from loguru import logger


def config_xmllib_logging() -> None:
    def colour_level_formatter(record) -> str:
        level = record["level"].name
        message = record["message"]
        function = record["function"]
        level_colors = {"INFO": "yellow", "WARNING": "red", "ERROR": "bold red"}
        if not (colour := level_colors.get(level)):
            colour = "white"
        return f"<{colour}>{level} | Function: '{function}' | {message}</{colour}>\n"

    logger.remove()
    logger.add(sys.stderr, colorize=True, format=colour_level_formatter)
