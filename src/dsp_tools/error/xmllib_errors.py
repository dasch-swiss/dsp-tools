from dsp_tools.error.exceptions import BaseError


class XmllibInputError(BaseError):
    """
    This error is raised if a user provided invalid input.
    """


class XmllibInternalError(BaseError):
    """
    This error is raised if an internal error, i.e. an error on which the user has no influence, is found in the xmllib.
    """
