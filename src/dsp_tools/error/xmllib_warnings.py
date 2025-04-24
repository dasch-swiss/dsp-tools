from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW


@dataclass
class MessageInfo:
    message: str
    resource_id: str
    prop_name: str | None = None


class XmllibUserInfoBase(Warning, ABC):
    """Base class for warnings that implement a custom showwarnings() function"""

    @classmethod
    @abstractmethod
    def showwarning(cls, message: str) -> None:
        """Functionality that should be executed when a warning of this class is emitted"""


class XmllibInputInfo(XmllibUserInfoBase):
    """If the xmllib input may be problematic"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        print(YELLOW + f"INFO | {message}" + RESET_TO_DEFAULT)


class XmllibInputWarning(XmllibUserInfoBase):
    """If the xmllib input is problematic"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        print(BOLD_RED + f"WARNING | {message}" + RESET_TO_DEFAULT)
