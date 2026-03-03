from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import UserError
from dsp_tools.setup.logger_config import LOGGER_SAVEPATH


class FatalNonOkApiResponseCode(BaseError):
    """This error is raised when the API gives an unexpected response, that we cannot anticipate and handle cleanly."""

    def __init__(self, request_url: str, status_code: int, response_text: str) -> None:
        resp_txt = response_text[:200] if len(response_text) > 200 else response_text
        msg = (
            f"We currently do not support the following API response code for this request.\n"
            f"Status code: {status_code}\n"
            f"Request URL: {request_url}\n"
            f"Original Response: {resp_txt}\n"
            f"Please contact support@dasch.swiss with the log file at {LOGGER_SAVEPATH}."
        )
        super().__init__(msg)


class InvalidInputError(UserError):
    """This error is raised if the API responds with a permanent error because of invalid input data"""


class ProjectOntologyNotFound(UserError):
    """Class for errors that are raised if a project is expected to have 1 or more ontologies, but none were found."""

    def __init__(self, shortcode: str) -> None:
        msg = f"The project with the shortcode '{shortcode}' does not have any ontologies."
        super().__init__(msg)


class ProjectNotFoundError(UserError):
    """Class if a project is expected to exist but could not be found."""


class MigrationExportExistsError(UserError):
    """Class if a migration for a project already exists."""

    def __init__(self) -> None:
        msg = (
            "An export for this project already exists on this server, it is not possible to have two exports. "
            "Either continue to download the export, or remove the export from the server "
            "with the command dsp-tools migration clean-up."
        )
        super().__init__(msg)


class MigrationImportExistsError(UserError):
    """Class if a migration for a project already exists."""

    def __init__(self) -> None:
        msg = (
            "An import for this project already exists on this server, it is not possible to have two imports. "
            "If you want to re-import the project you must first remove the import ID, "
            "with the command dsp-tools migration clean-up. And the project itself from the server. "
            "If you are on localhost you can also simply restart the stack with dsp-tools."
        )
        super().__init__(msg)


class MigrationExportImportInProgressError(UserError):
    """Class to raise if an import or export is in progress and the requested action is not possible."""

    def __init__(self, detail_msg: str) -> None:
        generic_msg = "An export or import is in progress on this server."
        super().__init__(f"{generic_msg} {detail_msg}")
