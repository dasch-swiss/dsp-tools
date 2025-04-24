from typing import runtime_checkable

from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW


@runtime_checkable
class XmllibUserInfo(Warning):
    """Protocol for warnings that implement a custom showwarnings() function"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Functionality that should be executed when a warning of this class is emitted"""


class XmllibInputInfo(XmllibUserInfo):
    """If the xmllib input may be problematic"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        print(YELLOW + f"INFO: {message}" + RESET_TO_DEFAULT)


class XmllibInputWarning(Warning):
    """If the xmllib input is problematic"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        print(BOLD_RED + f"WARNING: {message}" + RESET_TO_DEFAULT)
