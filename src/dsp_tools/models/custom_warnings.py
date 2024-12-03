from typing import Protocol
from typing import runtime_checkable

# These are ANSI escape codes which can be used to configure the print output on the terminal
# https://en.wikipedia.org/wiki/ANSI_escape_code
# All codes must start with "\033"
# The semicolon separates different configurations

BOLD_RED = "\033[1;31m"  # 1 (bold) ; 31 (red) m (finish or the sequence)
YELLOW = "\033[0;33m"  # 0 (normal font) ; 33 (yellow) m (finish or the sequence)
RESET_TO_DEFAULT = "\033[0m"  # reset the previous setting to default of the console


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
        """Print the warning, without context"""
        print(YELLOW + f"INFO: {message}" + RESET_TO_DEFAULT)


class DspToolsFutureWarning(FutureWarning):
    """Class for user-facing deprecation warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        print(BOLD_RED + f"DEPRECATION WARNING: {message}" + RESET_TO_DEFAULT)
