from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import UserError


class JSONFileParsingError(UserError):
    """This error should be raised if the user provided input file cannot be parsed."""


class DuplicateIdsInXmlAndId2IriMapping(UserError):
    """
    Represents an error raised if a resource ID that is in the Id2Iri mapping
    is also used as a resource id in the new data.
    """


class DspToolsRequestException(BaseError):
    """Class for errors that are raised if any request exceptions happens."""
