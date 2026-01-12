from dsp_tools.error.exceptions import BaseError


class ShaclValidationCliError(BaseError):
    """This error is raised when the validate data docker command has problems"""


class ShaclValidationError(BaseError):
    """This error is raised when an unexpected error occurs during the validation"""
