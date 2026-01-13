from dataclasses import dataclass
from pathlib import Path

from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.setup.logger_config import LOGGER_SAVEPATH


@dataclass
class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS.

    Attributes:
        message: A message that describes the error
    """

    message: str = ""

    def __str__(self) -> str:
        return self.message


class UserError(BaseError):
    """
    This is a base class for all the errors that are raised when the user input or set-up is faulty.
    The message should be as user-friendly as possible.
    """


class InputError(BaseError):
    """
    To be deprecated in favour of "UserError"
    This error is raised when the user input is invalid. The message should be as user-friendly as possible.
    """


class InternalError(BaseError):
    """
    Class for errors that are raised if the user cannot solve the problem themselves.
    """

    def __init__(self, custom_msg: str | None = None, keep_default_msg: bool = True) -> None:
        default_msg = (
            f"\n\n{BOLD_RED}An internal error occurred.{RESET_TO_DEFAULT}\n"
            "Please contact the dsp-tools development team (at support@dasch.swiss) with the following information:\n"
            "    - Which command was used.\n"
            "    - If applicable, any files that were used in conjunction with the command.\n"
            "    - A text file with the terminal output copied into.\n"
            f"    - The log file at {LOGGER_SAVEPATH}.\n"
        )
        match keep_default_msg, custom_msg:
            case False, str():
                super().__init__(custom_msg)
            case True, str():
                default_msg = f"\n\n{custom_msg}\n--------------------------{default_msg}"
                super().__init__(default_msg)
            case _:
                super().__init__(default_msg)


class UnreachableCodeError(BaseError):
    """Class that is raised if certain code is not reachable."""

    def __init__(self, msg: str | None = None) -> None:
        if not msg:
            msg = "This error should be unreachable, some bug is in the code."
        super().__init__(msg)


class UserFilepathNotFoundError(InputError):
    """This error is raised if a filepath from the user does not exist."""

    def __init__(self, filepath: str | Path) -> None:
        msg = f"The provided filepath does not exist: {filepath}"
        super().__init__(msg)


class UserDirectoryNotFoundError(InputError):
    """This error is raised if a directory from the user does not exist."""

    def __init__(self, directory: str | Path) -> None:
        msg = f"The provided directory does not exist: {directory}"
        super().__init__(msg)


class PermanentConnectionError(BaseError):
    """This error is raised when all attempts to reconnect to DSP have failed."""


class PermanentTimeOutError(BaseError):
    """This error is raised when python throws a timeout due to no response from the DSP-API."""


class BadCredentialsError(UserError):
    """This error is raised when DSP-API doesn't accept the provided credentials."""
