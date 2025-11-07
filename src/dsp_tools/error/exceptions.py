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
            "Please contact the dsp-tools development team (at info@dasch.swiss) with the following information:\n"
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


class DockerNotReachableError(BaseError):
    """This error is raised when docker is not running."""

    def __init__(self) -> None:
        msg = "Docker is not running properly. Please start Docker and try again."
        super().__init__(msg)


class DspApiNotReachableError(BaseError):
    """This error is raised when the DSP-API could not be reached on localhost."""


class DspToolsRequestException(BaseError):
    """Class for errors that are raised if any request exceptions happens."""


class InputError(BaseError):
    """This error is raised when the user input is invalid. The message should be as user-friendly as possible."""


class InvalidGuiAttributeError(BaseError):
    """This error is raised when a invalid gui-attribute is used."""


class FatalNonOkApiResponseCode(BaseError):
    """This error is raised when the API gives an unexpected response, that we cannot anticipate and handle cleanly."""

    def __init__(self, request_url: str, status_code: int, response_text: str) -> None:
        resp_txt = response_text[:200] if len(response_text) > 200 else response_text
        msg = (
            f"We currently do not support the following API response code for this request.\n"
            f"Status code: {status_code}\n"
            f"Request URL: {request_url}\n"
            f"Original Response: {resp_txt}\n"
            f"Please contact info@dasch.swiss with the log file at {LOGGER_SAVEPATH}."
        )
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


class JSONFileParsingError(InputError):
    """This error should be raised if the user provided input file cannot be parsed."""


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


class Id2IriReplacementError(BaseError):
    """Represents an error raised if an internal ID could not be found in the Id2Iri mapping."""


class DuplicateIdsInXmlAndId2IriMapping(InputError):
    """
    Represents an error raised if a resource ID that is in the Id2Iri mapping
    is also used as a resource id in the new data.
    """


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


class ProjectOntologyNotFound(BaseError):
    """Class for errors that are raised if a project is expected to have 1 or more ontologies, but none were found."""

    def __init__(self, shortcode: str) -> None:
        msg = f"The project with the shortcode '{shortcode}' does not have any ontologies."
        super().__init__(msg)


class CreateError(BaseError):
    """Errors for the create command."""


class ProjectNotFoundError(CreateError):
    """Class if a project is expected to exist but could not be found."""
