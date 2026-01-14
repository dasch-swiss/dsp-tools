from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class NoIngestFileFound(UserError):
    """no files have been uploaded for ingest"""


class IngestFailure(InternalError):
    """ingest call did not work"""
