from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class NoIngestFileFound(UserError):
    """no files have been uploaded for ingest"""


class InvalidIngestInputFilesError(UserError):
    """If the filepath provided for ingest are not valid"""


class IngestIdForFileNotFoundError(UserError):
    """If the filepath in the XML is not in the ingest mapping"""


class IngestFailure(InternalError):
    """ingest call did not work"""
