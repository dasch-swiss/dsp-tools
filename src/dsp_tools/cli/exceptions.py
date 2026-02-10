from dsp_tools.error.exceptions import UserError


class CliUserError(UserError):
    """Invalid user input in the CLI"""


class DockerNotReachableError(UserError):
    """This error is raised when docker is not running."""

    def __init__(self) -> None:
        msg = "Docker is not running properly. Please start Docker and try again."
        super().__init__(msg)


class DspApiNotReachableError(UserError):
    """This error is raised when the DSP-API could not be reached"""

    is_localhost: bool
    status_code: int | None
    response_text: str | None

    def __init__(
        self,
        is_localhost: bool,
        status_code: int | None = None,
        response_text: str | None = None,
    ) -> None:
        if is_localhost:
            base_msg = (
                "Cannot connect to the local DSP-API. "
                "Please check if your stack is healthy "
                "or start a stack with 'dsp-tools start-stack' if none is running."
            )
        else:
            base_msg = "Cannot connect to the remote DSP-API. Please contact the DaSCH engineering team for help."

        if status_code:
            base_msg += f"\nStatus code: {status_code}"
        if response_text:
            base_msg += f"\nResponse text: {response_text}"

        super().__init__(base_msg)
        self.is_localhost = is_localhost
        self.status_code = status_code
        self.response_text = response_text
