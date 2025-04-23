import sys
import warnings
from typing import TextIO

from loguru import logger

from dsp_tools.error.xmllib_warnings import XmllibUserMessage


def configure_logging() -> None:
    logger.remove()

    logger.remove()
    logger.add(
        sys.stderr,
        format="<level>{level} | Function: '{function}' | {message}</level>",
        colorize=True,
    )

    """
    This function makes sure that DSP-TOOLS internal warnings are displayed in their custom way how they specify it.
    This is done by monkeypatching the behavior of the warnings module, as officially recommended by the Python docs:
    https://docs.python.org/3/library/warnings.html#warnings.showwarning
    """

    def _custom_showwarning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        file: TextIO | None = None,
        line: str | None = None,
        depth: int = 2,
    ) -> None:
        if issubclass(category, XmllibUserMessage):
            category.showwarning(str(message), depth)
        else:
            pass

    warnings.showwarning = _custom_showwarning
