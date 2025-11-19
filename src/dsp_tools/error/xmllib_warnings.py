from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.ansi_colors import YELLOW


class UserMessageSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class MessageInfo:
    """
    message: message about what went wrong
    resource_id: ID of the affected resource
    prop_name: property name of the affected property (if applicable)
    field: information about which field of the resource is affected (if not the property), e.g. "resource id", "label"
    """

    message: str
    resource_id: str | None = None
    prop_name: str | None = None
    field: str | None = None


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
