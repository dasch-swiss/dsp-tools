from dataclasses import dataclass


@dataclass
class DspVreLibBaseError(Exception):
    """
    Base class of all errors of dsp-vre-lib.

    Attributes:
        message: A message that describes the error
    """

    message: str = ""

    def __str__(self) -> str:
        return self.message


class DspVreLibUserError(DspVreLibBaseError):
    """Base class of the errors that the user can solve, for example wrong input or wrong credentials."""


class DspVreLibInternalError(DspVreLibBaseError):
    """Base class of the errors that the user cannot solve."""


class BadCredentialsError(DspVreLibUserError):
    """This error is raised when DSP-API doesn't accept the provided credentials."""


class PermanentConnectionError(DspVreLibInternalError):
    """This error is raised when all attempts to reconnect to DSP have failed."""


class DspApiRequestError(DspVreLibInternalError):
    """This error is raised if an exception of the requests library occurs during an API call."""


class IngestError(DspVreLibInternalError):
    """ingest call did not work"""


class NoIngestFileFoundError(DspVreLibUserError):
    """no files have been uploaded for ingest"""


class FatalNonOkApiResponseCodeError(DspVreLibInternalError):
    """This error is raised when the API gives an unexpected response, that we cannot anticipate and handle cleanly."""

    def __init__(self, request_url: str, status_code: int, response_text: str) -> None:
        resp_txt = response_text[:200] if len(response_text) > 200 else response_text
        msg = (
            f"We currently do not support the following API response code for this request.\n"
            f"Status code: {status_code}\n"
            f"Request URL: {request_url}\n"
            f"Original Response: {resp_txt}\n"
            "Please contact support@dasch.swiss."
        )
        super().__init__(msg)


class InvalidInputError(DspVreLibUserError):
    """This error is raised if the API responds with a permanent error because of invalid input data"""


class InvalidIngestFileNameError(InvalidInputError):
    """This error is raised if INGEST rejects a file due to its name."""


class ProjectOntologyNotFoundError(DspVreLibUserError):
    """Class for errors that are raised if a project is expected to have 1 or more ontologies, but none were found."""

    def __init__(self, shortcode: str) -> None:
        msg = f"The project with the shortcode '{shortcode}' does not have any ontologies."
        super().__init__(msg)


class ProjectNotFoundError(DspVreLibUserError):
    """Class if a project is expected to exist but could not be found."""


class MigrationExportExistsError(DspVreLibUserError):
    """Class if an export for a project already exists."""

    def __init__(self) -> None:
        msg = (
            "An export for this project already exists on this server. "
            "It is not possible to create a second export before the first one has been downloaded. "
            "Either continue with downloading the export, or remove the export from the server "
            "with the command 'uvx dsp-tools migration clean-up'."
        )
        super().__init__(msg)


class MigrationImportExistsError(DspVreLibUserError):
    """Class if an import for a project already exists."""

    def __init__(self) -> None:
        msg = (
            "An import for this project already exists on this server. "
            "It is not possible to import the same project again. "
            "If you want to re-import the project, you must first remove the previous import "
            "with 'uvx dsp-tools migration clean-up', and then delete the project itself from the server. "
            "If you are on localhost, you can also simply restart the stack with 'uvx dsp-tools start-stack'."
        )
        super().__init__(msg)


class MigrationExportImportInProgressError(DspVreLibUserError):
    """Class to raise if an import or export is in progress and the requested action is not possible."""

    def __init__(self, detail_msg: str) -> None:
        generic_msg = "An export or import is in progress on this server."
        super().__init__(f"{generic_msg} {detail_msg}")
