from typing import Protocol
from typing import runtime_checkable

from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW


@runtime_checkable
class DspToolsWarning(Protocol):
    """Protocol for warnings that implement a custom showwarnings() function"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Functionality that should be executed when a warning of this class is emitted"""


class DspToolsUserWarning(Warning):
    """Class for general user-facing warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        print(BOLD_RED + f"WARNING: {message}" + RESET_TO_DEFAULT)


class DspToolsUserInfo(Warning):
    """Class for general user-facing warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the information, without context"""
        print(YELLOW + f"INFO: {message}" + RESET_TO_DEFAULT)


class DspToolsFutureWarning(FutureWarning):
    """Class for user-facing deprecation warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        print(BOLD_RED + f"DEPRECATION WARNING: {message}" + RESET_TO_DEFAULT)
