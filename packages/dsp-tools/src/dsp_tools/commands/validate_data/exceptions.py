from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class ShaclValidationCliError(InternalError):
    """This error is raised when the validate data docker command has problems"""

    def __init__(self, returncode: int, stdout: str, stderr: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        msg = (
            "Data validation Docker command failed. "
            "Please ensure Docker is running and try again. "
            f"Exit code: {self.returncode}"
        )
        if self.stdout:
            msg += f"\nStdout: {self.stdout}"
        if self.stderr:
            msg += f"\nStderr: {self.stderr}"
        super().__init__(msg, keep_default_msg=True)


class ShaclValidationOutOfMemoryError(UserError):
    """This error is raised when the validate data docker command (most likely) ran out of memory"""

    def __init__(self, docker_memory_bytes: int | None) -> None:
        msg = "The data validation in Docker stopped, most likely because it ran out of memory."
        if docker_memory_bytes:
            msg += f" Docker reports {docker_memory_bytes / 1024**3:.1f} GB of memory."
        msg += (
            "\nIncrease the memory that Docker may use (Docker Desktop: Settings > Resources > Memory) "
            "and try again, or split the XML file into smaller files."
        )
        super().__init__(msg)


class ShaclValidationError(InternalError):
    """This error is raised when an unexpected error occurs during the validation"""


class FootnoteNotParsableError(UserError):
    """This error is raised when the content of a richtext cannot be parsed."""

    def __init__(self, res_id: str, footnote_str: str) -> None:
        msg = (
            "Your footnotes contain XML syntax errors, for example an unclosed tag. "
            "This must be fixed before validation can continue.\n"
            f"Resource ID: {res_id}, Original text: {footnote_str}"
        )
        super().__init__(msg)
