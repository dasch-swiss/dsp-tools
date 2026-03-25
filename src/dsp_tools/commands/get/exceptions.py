from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class UnknownDOAPException(InternalError):
    """Class for errors that are raised if a DOAP cannot be parsed"""


class InvalidProjectIdentifierError(UserError):
    """This error is raised when the provided project identifier is not a valid shortcode, shortname, or IRI."""
