import sys
import warnings
from typing import TextIO

from loguru import logger

from dsp_tools.error.xmllib_warnings import XmllibUserMessage


def xmllib_warning_config() -> None:
    """
    This function makes sure that DSP-TOOLS internal warnings are displayed in their custom way how they specify it.
    This is done by monkeypatching the behavior of the warnings module, as officially recommended by the Python docs:
    https://docs.python.org/3/library/warnings.html#warnings.showwarning
    """

    built_in_showwarning = warnings.showwarning

    def _custom_showwarning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        file: TextIO | None = None,
        line: str | None = None,
    ) -> None:
        if issubclass(category, XmllibUserMessage):
            category.showwarning(str(message))
        else:
            built_in_showwarning(message, category, filename, lineno, file, line)

    warnings.showwarning = _custom_showwarning


def config_xmllib_logging() -> None:
    def colour_level_formatter(record) -> str:
        level = record["level"].name
        message = record["message"]
        func = ":"
        if not (fnc := record["function"]) == "<module>":
            func = f":{fnc}:"
        function = f"{record['file'].name}{func}{record['line']}"
        level_colors = {"INFO": "yellow", "WARNING": "red", "ERROR": "bold red"}
        if not (colour := level_colors.get(level)):
            colour = "white"
        return f"<{colour}>{level} | Function: '{function}' | {message}</{colour}>\n"

    logger.remove()
    logger.add(sys.stderr, colorize=True, format=colour_level_formatter)
