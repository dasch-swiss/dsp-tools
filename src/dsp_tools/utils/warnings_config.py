import warnings
from typing import TextIO

from dsp_tools.models.custom_warnings import DspToolsWarning


def initialize_warnings() -> None:
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
        if issubclass(category, DspToolsWarning):
            category.showwarning(str(message))
        else:
            built_in_showwarning(message, category, filename, lineno, file, line)

    warnings.showwarning = _custom_showwarning
