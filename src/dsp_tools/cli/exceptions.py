from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class DockerNotReachableError(UserError):
    """This error is raised when docker is not running."""

    def __init__(self) -> None:
        msg = "Docker is not running properly. Please start Docker and try again."
        super().__init__(msg)


class DspApiNotReachableError(UserError):
    """This error is raised when the DSP-API could not be reached on localhost."""


class StartStackInputError(InternalError):
    """An input to start the stack is invalid"""


class FusekiStartUpError(InternalError):
    """A problem with Fuseki happened during the start"""
