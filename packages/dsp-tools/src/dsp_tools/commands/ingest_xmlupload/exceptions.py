from pathlib import Path
from typing import ClassVar

from dsp_tools.error.exceptions import UserError

MIB = 1024 * 1024
DEFAULT_SERVER_LIMIT_BYTES = 250 * MIB


class InvalidIngestInputFilesError(UserError):
    """If one or more filepaths provided to ingest are not valid"""


class IngestIdForFileNotFoundError(UserError):
    """If the filepath in the XML is not in the ingest mapping"""


class NoFilesUploadedForIngestError(UserError):
    """The ingest server has no uploaded files for the project."""

    def __init__(self, server_message: str) -> None:
        super().__init__(
            f"{server_message} Before using the 'ingest-files' command, "
            "you must upload some files with the 'upload-files' command."
        )


class ForeignShortcodeIriError(UserError):
    """Resources have a preset IRI that belongs to a different project than the one being uploaded to."""

    def __init__(self, shortcode: str, resource_iris: dict[str, str]) -> None:
        listing = "\n".join(f"  - Resource ID '{res_id}': {iri}" for res_id, iri in resource_iris.items())
        super().__init__(
            f"The following resources have an IRI that does not belong to the project with shortcode '{shortcode}':\n"
            f"{listing}\n"
            f"Please correct the ARKs or IRIs of these resources so that they contain the shortcode '{shortcode}'."
        )


def delete_command(shortcode: str, import_id: str) -> str:
    return f"uvx dsp-tools delete-data-import {shortcode} {import_id}"


def describe_task_left_on_server(shortcode: str, import_id: str, payload: Path, id2iri: Path) -> str:
    """The text for a bulk data import whose task stays on the server."""
    return (
        f"The bulk data import with the ID '{import_id}' stays on the server, and may still complete.\n"
        f"The payload file is kept at: {payload}\n"
        f"The mapping of internal IDs to IRIs is kept at: {id2iri}\n"
        f"This bulk data import blocks further imports of this project until you remove it with: "
        f"{delete_command(shortcode, import_id)}"
    )


class SystemAdminRequiredError(UserError):
    """The login failed, or the user is not a system admin."""

    def __init__(self, command: str) -> None:
        super().__init__(f"The login failed, or the user is not a system admin. Only system admins can run {command}.")


class OnBehalfOfUserMissingError(UserError):
    """The user of '--on-behalf-of-user' does not exist on the server."""

    def __init__(self, user: str) -> None:
        super().__init__(f"The user '{user}' given with '--on-behalf-of-user' does not exist on the server.")


class OnBehalfOfUserRejectedError(UserError):
    """The user of '--on-behalf-of-user' cannot own the imported data."""

    _REASONS: ClassVar[dict[str, str]] = {
        "is_system_admin": "is a system admin. Choose a project user who is not a system admin.",
        "not_project_member": "is not a member of the project.",
        "inactive": "is not active.",
        "cannot_create": "has no create rights in the project.",
        "malformed_identifier": "is neither an email nor a username.",
    }

    def __init__(self, user: str, reason: str) -> None:
        explanation = self._REASONS.get(reason, f"cannot be used (reason given by the server: '{reason}').")
        super().__init__(f"The user '{user}' given with '--on-behalf-of-user' {explanation}")


def _describe_size(size_bytes: int, max_bytes: int | None) -> str:
    if max_bytes is None:
        limit = f"The default server limit is {DEFAULT_SERVER_LIMIT_BYTES / MIB:.0f} MiB."
    else:
        limit = f"The server accepts at most {max_bytes / MIB:.0f} MiB."
    return f"The size of your bulk data import is {size_bytes / MIB:.1f} MiB. {limit}"


class PayloadTooLargeError(UserError):
    """The server rejects the payload because it is too large."""

    def __init__(self, size_bytes: int, max_bytes: int | None) -> None:
        super().__init__(
            f"The server rejected the payload because it is too large. {_describe_size(size_bytes, max_bytes)}"
        )


class PayloadSendConnectionLostError(UserError):
    """The connection to the server ended during the upload of the payload."""

    def __init__(self, size_bytes: int) -> None:
        super().__init__(
            "The connection to the server ended during the upload of the payload. "
            "The server closes the connection if the payload is too large. "
            f"{_describe_size(size_bytes, None)}\n"
            "If the payload is smaller, the server may still process this bulk data import. "
            "A new run reports it with its ID."
        )


class PayloadSendServerError(UserError):
    """The server answered the upload of the payload with an unexpected error, for example a gateway timeout."""

    def __init__(self, reason: str, payload: Path, id2iri: Path) -> None:
        super().__init__(
            f"The server answered the upload of the payload with an error:\n{reason}\n"
            "The server may still process this bulk data import. A new run reports it with its ID.\n"
            f"The payload file is kept at: {payload}\n"
            f"The mapping of internal IDs to IRIs is kept at: {id2iri}"
        )


class BulkImportExistsError(UserError):
    """A bulk data import task exists for the project."""

    def __init__(self, shortcode: str, import_id: str) -> None:
        super().__init__(
            f"A bulk data import already exists for the project '{shortcode}' (import ID '{import_id}'). "
            f"It was not deleted. Remove it with: {delete_command(shortcode, import_id)}"
        )


class BulkImportRunningError(UserError):
    """Another import runs on the server."""

    def __init__(self) -> None:
        super().__init__("Another import (bulk or migration) is running on this server. Try again later.")


class BulkImportPreconditionError(UserError):
    """The project is not in a state that permits a bulk data import."""

    def __init__(self, error_code: str, server_message: str, data_imports_folder: Path) -> None:
        msg = server_message
        if error_code == "data_graph_exists":
            msg += (
                "\nThe project must hold no data except list nodes. "
                "An earlier import of this project may have completed: "
                f"its '_id2iri.json' file is in the folder {data_imports_folder}"
            )
        super().__init__(msg)


class BulkImportNotEnabledError(UserError):
    """The server has the bulk data import turned off."""

    def __init__(self) -> None:
        super().__init__("The bulk data import is not enabled on this server.")


class BulkImportStatusUnknownError(UserError):
    """The status of the bulk data import task could not be read, so the task may stay on the server."""

    def __init__(self, reason: str, shortcode: str, import_id: str, payload: Path, id2iri: Path) -> None:
        super().__init__(
            f"The status of the bulk data import could not be read: {reason}\n"
            + describe_task_left_on_server(shortcode, import_id, payload, id2iri)
        )
