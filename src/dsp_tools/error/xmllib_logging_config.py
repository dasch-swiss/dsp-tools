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
        level_colors = {"INFO": "yellow", "WARNING": "red", "ERROR": "bold red"}
        if not (colour := level_colors.get(level)):
            colour = "white"
        message = record["message"]
        msg_list = [f"<{colour}>{level}"]
        if not (fnc := record["function"]) == "<module>":
            func = f":{fnc}:"
            if not (f_name := record['file'].name) == "pydevd.py":
                function = f"{f_name}{func}{record['line']}"
                msg_list.append(f"Function: '{function}'")
        msg_list.append(f"{message}</{colour}>\n")
        return " | ".join(msg_list)

    logger.remove()
    logger.add(sys.stderr, colorize=True, format=colour_level_formatter)
