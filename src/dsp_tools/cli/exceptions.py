from dsp_tools.error.exceptions import UserError


class CliUserError(UserError):
    """Invalid user input in the CLI"""


class DockerNotReachableError(UserError):
    """This error is raised when docker is not running."""

    def __init__(self) -> None:
        msg = "Docker is not running properly. Please start Docker and try again."
        super().__init__(msg)


class DspApiNotReachableError(UserError):
    """This error is raised when the DSP-API could not be reached on localhost."""
