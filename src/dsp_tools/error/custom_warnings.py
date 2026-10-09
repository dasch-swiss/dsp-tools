from abc import ABC
from abc import abstractmethod

from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


class DspToolsWarning(Warning, ABC):
    """Abstract base class for warnings that implement a custom showwarnings() function"""

    @classmethod
    @abstractmethod
    def showwarning(cls, message: str) -> None:
        """Functionality that should be executed when a warning of this class is emitted"""


class DspToolsUserWarning(DspToolsWarning):
    """Class for general user-facing warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        print(BOLD_RED + f"WARNING: {message}" + RESET_TO_DEFAULT)


class DspToolsMissingAdminAccountWarning(DspToolsUserWarning):
    """Class to display warning that an admin account is missing."""

    def __init__(self, specifics_to_upload: str) -> None:
        generic = (
            "It is mandatory that each project has an admin account for DaSCH internal usage. "
            "The account must be in the format of [shortname]@admin.dasch.swiss "
            "and must be used for all data uploads on prod like server. "
            "Other accounts are only permitted in test environments."
        )
        self.message = f"{specifics_to_upload}\n{generic}"


class DspToolsFutureWarning(DspToolsWarning, FutureWarning):
    """Class for user-facing deprecation warnings"""

    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        print(BOLD_RED + f"DEPRECATION WARNING: {message}" + RESET_TO_DEFAULT)


class DspToolsUnexpectedStatusCodeWarning(DspToolsWarning):
    @classmethod
    def showwarning(cls, message: str) -> None:
        """Print the warning, without context"""
        print(BOLD_RED + f"ERROR: {message}" + RESET_TO_DEFAULT)
