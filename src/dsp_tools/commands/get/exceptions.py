from dsp_tools.error.exceptions import UserError


class InvalidProjectIdentifierError(UserError):
    """This error is raised when the provided project identifier is not a valid shortcode, shortname, or IRI."""
