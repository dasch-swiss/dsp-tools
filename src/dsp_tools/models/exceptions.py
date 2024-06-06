from dataclasses import dataclass
from pathlib import Path


@dataclass
class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS.

    Attributes:
        message: A message that describes the error
    """

    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class Excel2JsonListError(BaseError):
    """
    Class for errors that are raised in the context of the excel2json ListNode class.
    """


class InternalError(BaseError):
    """
    Class for errors that are raised if the user cannot solve the problem themselves.
    """

    def __init__(self, custom_msg: str | None = None, keep_default_msg: bool = True) -> None:
        default_msg = (
            "\n\nAn internal error occurred.\n"
            "Please contact the dsp-tools development team with the following information:\n"
            "    - Which command was used.\n"
            "    - If applicable, any files that were used in conjunction with the command.\n"
            "    - A file with the terminal output copied into.\n"
            "    - The log files called 'logging.log', if there are several, include all.\n"
            f"      They can be found at: {Path.home() / Path('.dsp-tools')}\n"
        )
        match keep_default_msg, custom_msg:
            case False, str():
                super().__init__(custom_msg)
            case True, str():
                default_msg = f"\n\n{custom_msg}\n--------------------------{default_msg}"
                super().__init__(default_msg)
            case _:
                super().__init__(default_msg)


class PermissionNotExistsError(BaseError):
    """Class for errors that are raised when a permission does not exist."""


class InputError(BaseError):
    """Class for errors that is called when the user input is invalid."""


class UserError(BaseError):
    """
    Class for errors that are intended for user feedback.
    Typically, a UserError is raised when the execution of a program must be interrupted
    due to a bad condition in the input data that prevents further processing.
    The message should be as user-friendly as possible.
    """


class PermanentConnectionError(BaseError):
    """This error is raised when all attempts to reconnect to DSP have failed."""


class InvalidInputError(BaseError):
    """This error is raised if the API responds with a permanent error because of invalid input data"""


class PermanentTimeOutError(BaseError):
    """This error is raised when python throws a timeout due to no response from the DSP-API."""


class BadCredentialsError(PermanentConnectionError):
    """This error is raised when DSP-API doesn't accept the prodived credentials."""


class XmlUploadError(BaseError):
    """Represents an error raised in the context of the xmlupload."""


class XmlUploadInterruptedError(XmlUploadError):
    """Represents an error raised when the xmlupload was interrupted."""
