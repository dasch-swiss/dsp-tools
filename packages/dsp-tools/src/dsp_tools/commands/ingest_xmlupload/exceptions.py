from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


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


class ResourceIriMissingError(InternalError):
    """A resource has no IRI when the payload of the bulk data import is written."""

    def __init__(self, res_id: str) -> None:
        super().__init__(f"The resource '{res_id}' has no IRI.")
