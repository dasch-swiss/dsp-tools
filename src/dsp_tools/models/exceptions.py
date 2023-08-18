import json
from typing import Optional
from dataclasses import dataclass

import regex


@dataclass
class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS.
    All other error classes should inherit from this class.

    Attributes:
        message: A message that describes the error
    """

    message: str


@dataclass
class UserError(BaseError):
    """
    Error that is intended for user feedback.
    Typically, a UserError is raised when the execution of a program must be interrupted
    due to a bad condition in the input data that prevents further processing.
    The message should be as user-friendly as possible.
    The message wil be printed to console (without stack trace),
    then Python will quit.
    """

    message: str


@dataclass
class InternalError(BaseError):
    """
    Error that will be handled by a higher level function.
    """


@dataclass
class DspApiError(InternalError):
    """
    Error that originates from DSP-API.

    Attributes:
        message: A message that describes the error
        status_code: HTTP status code of the response from DSP-API
        json_content_of_api_response: The message that DSP-API returns
        orig_err_msg_from_api: Original error message that DSP-API returns
        reason_from_api: Reason for the failure that DSP-API returns
        api_route: The route that was called
    """

    message: str
    status_code: Optional[int] = None
    json_content_of_api_response: Optional[str] = None
    orig_err_msg_from_api: Optional[str] = None
    reason_from_api: Optional[str] = None
    api_route: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.json_content_of_api_response:
            return
        try:
            parsed_json = json.loads(self.json_content_of_api_response)
        except json.JSONDecodeError:
            parsed_json = {}
        knora_api_error = parsed_json.get("knora-api:error", "")
        knora_api_error = regex.sub(r"^dsp\.errors\.[A-Za-z]+?: ?", "", knora_api_error)
        self.orig_err_msg_from_api = knora_api_error or None


@dataclass
class XmlError(InternalError):
    """Error raised in the context of the XML import"""

    message: str
