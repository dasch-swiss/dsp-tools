from dsp_tools.error.exceptions import InternalError


class StartStackInputError(InternalError):
    """An input to start the stack is invalid"""


class FusekiStartUpError(InternalError):
    """A problem with Fuseki happened during the start"""
