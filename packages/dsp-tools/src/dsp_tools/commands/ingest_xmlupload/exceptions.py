from dsp_tools.error.exceptions import UserError


class InvalidIngestInputFilesError(UserError):
    """If one or more filepaths provided to ingest are not valid"""


class IngestIdForFileNotFoundError(UserError):
    """If the filepath in the XML is not in the ingest mapping"""


class NoFilesUploadedForIngestError(UserError):
    """The ingest service has no uploaded files for the project."""

    def __init__(self, server_message: str) -> None:
        super().__init__(
            f"{server_message} Before using the 'ingest-files' command, "
            "you must upload some files with the 'upload-files' command."
        )
