import json
import re
from typing import Optional


class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS.

    Attributes:
        message: A message that describes the error
        status_code: HTTP status code of the response from DSP-API (only applicable if the error comes from DSP-API)
        json_content_of_api_response: The message that DSP-API returns (only applicable if the error comes from DSP-API)
        original_error_msg_from_api: The original error message that DSP-API returns (only applicable if the error comes from DSP-API)
        reason_from_api_response: The reason for the failure that DSP-API returns (only applicable if the error comes from DSP-API)
        api_route: The route that was called (only applicable if the error comes from DSP-API)
    """
    message: str
    status_code: Optional[int]
    json_content_of_api_response: Optional[str]
    original_error_msg_from_api: Optional[str] = None
    reason_from_api_response: Optional[str]
    api_route: Optional[str]

    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        json_content_of_api_response: Optional[str] = None,
        reason_from_api_response: Optional[str] = None,
        api_route: Optional[str] = None
    ) -> None:
        """
        A basic error class for DSP-TOOLS.

        Args:
            message: A message that describes the error
            status_code: HTTP status code of the response from DSP-API (only applicable if the error comes from DSP-API)
            json_content_of_api_response: The message that DSP-API returns (only applicable if the error comes from DSP-API)
            reason_from_api_response: The reason for the failure that DSP-API returns (only applicable if the error comes from DSP-API)
            api_route: The route that was called (only applicable if the error comes from DSP-API)
        """
        super().__init__()
        self.message = message
        self.status_code = status_code
        if json_content_of_api_response:
            self.json_content_of_api_response = json_content_of_api_response
            try:
                parsed_json = json.loads(json_content_of_api_response)
                if "knora-api:error" in parsed_json:
                    knora_api_error = parsed_json["knora-api:error"]
                    knora_api_error = re.sub(r"^dsp\.errors\.[A-Za-z]+?: ?", "", knora_api_error)
                    self.original_error_msg_from_api = knora_api_error
            except json.JSONDecodeError:
                pass
        self.reason_from_api_response = reason_from_api_response
        self.api_route = api_route
    
    def __str__(self) -> str:
        return self.message


class InternalError(BaseError):
    """
    Class for errors that will be handled by a higher level function
    """
    pass


class UserError(BaseError):
    """
    Class for errors that are intended for user feedback. 
    Typically, a UserError is raised when the execution of a program must be interrupted 
    due to a bad condition in the input data that prevents further processing.
    The message should be as user-friendly as possible.
    """
    pass
