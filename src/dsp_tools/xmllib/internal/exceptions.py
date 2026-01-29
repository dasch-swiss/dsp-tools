from dsp_tools.error.exceptions import UserError


class XmllibInputError(UserError):
    """
    This error is raised if a user provided invalid input.
    It should never be raised plain, but with the dedicated util function.
    """


class XmllibFileNotFoundError(UserError):
    """
    This error is raised if a user provided a filepath that does not exist.
    """


class XmllibInternalError(UserError):
    """
    This error is raised if an internal error, i.e. an error on which the user has no influence, is found in the xmllib.
    """
