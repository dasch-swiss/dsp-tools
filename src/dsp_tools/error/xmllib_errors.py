from dsp_tools.error.exceptions import BaseError


class XmllibInputError(BaseError):
    """
    This error is raised if a user provided invalid input.
    It should never be raised plain, but with the dedicated util function.
    """


class XmllibFileNotFoundError(BaseError):
    """
    This error is raised if a user provided a filepath that does not exist.
    """


class XmllibInternalError(BaseError):
    """
    This error is raised if an internal error, i.e. an error on which the user has no influence, is found in the xmllib.
    """
