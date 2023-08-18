from typing import Optional
from dataclasses import dataclass


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
        message: The original message (JSON string) that DSP-API returns
        status_code: HTTP status code of the response from DSP-API
        reason: Reason for the failure that DSP-API returns
        api_route: The route that was called
    """

    message: str
    status_code: Optional[int] = None
    reason: Optional[str] = None
    api_route: Optional[str] = None


@dataclass
class XmlError(InternalError):
    """Error raised in the context of the XML import"""

    message: str
