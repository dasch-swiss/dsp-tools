from typing import Protocol
from typing import runtime_checkable

from termcolor import cprint


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
        cprint(f"WARNING: {message}", color="red", attrs=["bold"])


class DspToolsFutureWarning(FutureWarning):
    """Class for user-facing deprecation warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        cprint(f"DEPRECATION WARNING: {message}", color="red", attrs=["bold"])
