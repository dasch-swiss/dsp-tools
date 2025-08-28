from dataclasses import dataclass
from pathlib import Path

from dsp_tools.config.logger_config import LOGGER_SAVEPATH
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


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


class InternalError(BaseError):
    """
    Class for errors that are raised if the user cannot solve the problem themselves.
    """

    def __init__(self, custom_msg: str | None = None, keep_default_msg: bool = True) -> None:
        default_msg = (
            f"\n\n{BOLD_RED}An internal error occurred.{RESET_TO_DEFAULT}\n"
            "Please contact the dsp-tools development team with the following information:\n"
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


class InputError(BaseError):
    """This error is raised when the user input is invalid. The message should be as user-friendly as possible."""


class UserFilepathNotFoundError(InputError):
    """This error is raised if a filepath from the user does not exist."""

    def __init__(self, filepath: str | Path) -> None:
        msg = f"The provided filepath does not exist: {filepath}"
        super().__init__(msg)


class PermanentConnectionError(BaseError):
    """This error is raised when all attempts to reconnect to DSP have failed."""


class InvalidInputError(BaseError):
    """This error is raised if the API responds with a permanent error because of invalid input data"""


class ShaclValidationCliError(BaseError):
    """This error is raised when the validate data docker command has problems"""


class ShaclValidationError(BaseError):
    """This error is raised when an unexpected error occurs during the validation"""


class InvalidIngestFileNameError(InvalidInputError):
    """This error is raised if INGEST rejects a file due to its name."""


class PermanentTimeOutError(BaseError):
    """This error is raised when python throws a timeout due to no response from the DSP-API."""


class BadCredentialsError(PermanentConnectionError):
    """This error is raised when DSP-API doesn't accept the prodived credentials."""


class XmlUploadError(BaseError):
    """Represents an error raised in the context of the xmlupload."""


class XmlInputConversionError(BaseError):
    """Represents an error raised in the context of the xmlupload."""


class XmlUploadInterruptedError(XmlUploadError):
    """Represents an error raised when the xmlupload was interrupted."""


class XmlUploadPermissionsNotFoundError(BaseError):
    """Class for errors that are raised when a permission does not exist."""


class XmlUploadAuthorshipsNotFoundError(BaseError):
    """Class for errors that are raised when an authorship id does not exist."""


class XmlUploadListNodeNotFoundError(BaseError):
    """Class for errors that are raised when a list node does not exist."""


class UnknownDOAPException(BaseError):
    """Class for errors that are raised if a DOAP cannot be parsed"""
