from dsp_tools.error.exceptions import UserError


class JSONFileParsingError(UserError):
    """This error should be raised if the user provided input file cannot be parsed."""
