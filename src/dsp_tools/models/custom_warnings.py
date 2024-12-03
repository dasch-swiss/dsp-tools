from typing import Protocol
from typing import runtime_checkable

# These are ANSI escape codes which can be used to configure the print output on the terminal
# https://en.wikipedia.org/wiki/ANSI_escape_code
# All codes must start with "\033"
# The semicolon separates different configurations
# the "m" at the end signals,
# that the configuration code it finished and after that the string that should be printed starts

BOLD_RED = "\033[1;31m"  # 1 (bold) ; 31 (red)
YELLOW = "\033[0;33m"  # 0 (normal font) ; 33 (yellow)
RESET_TO_DEFAULT = "\033[0m"  # reset the previous setting to the default of the console


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
