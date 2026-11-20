from dsp_tools.error.exceptions import UserError


class InvalidIngestInputFilesError(UserError):
    """If one or more filepaths provided to ingest are not valid"""


class IngestIdForFileNotFoundError(UserError):
    """If the filepath in the XML is not in the ingest mapping"""
