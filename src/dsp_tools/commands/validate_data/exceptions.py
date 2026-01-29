from dsp_tools.error.exceptions import InternalError


class ShaclValidationCliError(InternalError):
    """This error is raised when the validate data docker command has problems"""

    def __init__(self, returncode: int, stderr: str) -> None:
        self.returncode = returncode
        self.stderr = stderr
        msg = (
            "Data validation Docker command failed. "
            "Please ensure Docker Desktop is running and try again. "
            f"Exit code: {self.returncode}"
        )
        if self.stderr:
            msg += f"\nStderr: {self.stderr[:400]}"
        super().__init__(msg, keep_default_msg=True)


class ShaclValidationError(InternalError):
    """This error is raised when an unexpected error occurs during the validation"""
