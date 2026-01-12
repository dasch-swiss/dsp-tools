from dsp_tools.error.exceptions import BaseError


class UnknownDOAPException(BaseError):
    """Class for errors that are raised if a DOAP cannot be parsed"""
