from dsp_tools.error.exceptions import InternalError


class ShaclValidationCliError(InternalError):
    """This error is raised when the validate data docker command has problems"""


class ShaclValidationError(InternalError):
    """This error is raised when an unexpected error occurs during the validation"""
