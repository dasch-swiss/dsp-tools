from dsp_tools.error.exceptions import InternalError


class UnknownDOAPException(InternalError):
    """Class for errors that are raised if a DOAP cannot be parsed"""
