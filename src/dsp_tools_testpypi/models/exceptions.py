import contextlib
import json
from pathlib import Path
from typing import Optional

import regex


class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS.

    Attributes:

        message: A message that describes the error
        status_code: HTTP status code of the response from DSP-API (only applicable if error comes from DSP-API)
        json_content_of_api_response: The message that DSP-API returns (only applicable if error comes from DSP-API)
        orig_err_msg_from_api: Original error message that DSP-API returns (only applicable if error comes from DSP-API)
        reason_from_api: Reason for the failure that DSP-API returns (only applicable if error comes from DSP-API)
        api_route: The route that was called (only applicable if the error comes from DSP-API)
    """

    message: str
    status_code: Optional[int]
    json_content_of_api_response: Optional[str]
    orig_err_msg_from_api: Optional[str] = None
    reason_from_api: Optional[str]
    api_route: Optional[str]

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        json_content_of_api_response: Optional[str] = None,
        reason_from_api: Optional[str] = None,
        api_route: Optional[str] = None,
    ) -> None:
        """
        A basic error class for DSP-TOOLS.

        Args:
            message: A message that describes the error
            status_code: HTTP status code of the response from DSP-API (only applicable if error comes from DSP-API)
            json_content_of_api_response: The message that DSP-API returns (only applicable if error comes from DSP-API)
            reason_from_api: Reason for the failure that DSP-API returns (only applicable if error comes from DSP-API)
            api_route: The route that was called (only applicable if the error comes from DSP-API)
        """
        super().__init__()
        self.message = message
        self.status_code = status_code
        if json_content_of_api_response:
            self.json_content_of_api_response = json_content_of_api_response
            with contextlib.suppress(json.JSONDecodeError):
                parsed_json = json.loads(json_content_of_api_response)
                if "knora-api:error" in parsed_json:
                    knora_api_error = parsed_json["knora-api:error"]
                    knora_api_error = regex.sub(r"^dsp\.errors\.[A-Za-z]+?: ?", "", knora_api_error)
                    self.orig_err_msg_from_api = knora_api_error
        self.reason_from_api = reason_from_api
        self.api_route = api_route

    def __str__(self) -> str:
        return self.message


class InternalError(BaseError):
    """
    Class for errors that are raised if the user cannot solve the problem themselves.
    """

    def __init__(self, custom_msg: str | None = None, keep_default_msg: bool = True) -> None:
        default_msg = (
            "\n\nAn internal error occurred.\n"
            "Please contact the dsp-tools development team with the following information:\n"
            "    - Which command was used.\n"
            "    - If applicable, any files that were used in conjunction with the command.\n"
            "    - A file with the terminal output copied into.\n"
            "    - The log files called 'logging.log', if there are several, include all.\n"
            f"      They can be found at: {Path.home() / Path('.dsp-tools')}\n"
        )
        match keep_default_msg, custom_msg:
            case False, str():
                super().__init__(custom_msg)  # type: ignore[arg-type]
            case True, str():
                default_msg = f"\n\n{custom_msg}\n--------------------------{default_msg}"
                super().__init__(default_msg)
            case _:
                super().__init__(default_msg)


class RetryError(BaseError):
    """
    A class for errors where the user should try again later.
    """

    def __init__(self, custom_msg: str | None = None, keep_default_msg: bool = True) -> None:
        default_msg = (
            "\n\nAn internal error occurred.\n"
            "Please contact the dsp-tools development team with the following information:\n"
            "    - Which command was used.\n"
            "    - If applicable, any files that were used in conjunction with the command.\n"
            "    - A file with the terminal output copied into.\n"
            "    - The log files called 'logging.log', if there are several, include all.\n"
            f"     They can be found at: {Path.home() / Path('.dsp-tools')}\n"
        )
        match keep_default_msg, custom_msg:
            case False, str():
                super().__init__(custom_msg)  # type: ignore[arg-type]
            case True, str():
                default_msg = f"\n\n{custom_msg}\n--------------------------{default_msg}"
                super().__init__(default_msg)
            case _:
                super().__init__(default_msg)


class InputError(BaseError):
    """
    Class for errors that is called when the user input is invalid.
    """


class UserError(BaseError):
    """
    Class for errors that are intended for user feedback.
    Typically, a UserError is raised when the execution of a program must be interrupted
    due to a bad condition in the input data that prevents further processing.
    The message should be as user-friendly as possible.
    """


class XmlUploadError(Exception):
    """
    Represents an error raised in the context of the XML import.
    """

    _message: str

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self) -> str:
        return f"XML-ERROR: {self._message}"
