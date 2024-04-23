from typing import Protocol
from typing import runtime_checkable

from termcolor import colored


@runtime_checkable
class DspToolsWarning(Protocol):
    """Protocol for warnings that implement a custom showwarnings() function"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Functionality that should be executed when a warning of this class is emitted"""
        ...


class DspToolsFutureWarning(FutureWarning):
    """Class for user-facing deprecation warnings"""

    def __str__(self) -> str:
        return colored(self.args[0], color="red", attrs=["bold"])

    @classmethod
    def showwarning(cls, message: str) -> None:
        """"""
        print(message)
