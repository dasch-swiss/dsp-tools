import json
import re
from typing import Optional


class BaseError(Exception):
    """
    A basic error class for DSP-TOOLS
    """
    message: str
    status_code_of_api_response: Optional[int]
    original_error_message_from_api: Optional[str]
    reason_for_failure_from_api_response: Optional[str]
    api_route: Optional[str]

    def __init__(
        self, 
        message: str, 
        status_code_of_api_response: Optional[int] = None,
        json_content_of_api_response: Optional[str] = None,
        reason_for_failure_from_api_response: Optional[str] = None,
        api_route: Optional[str] = None
    ) -> None:
        super().__init__()
        self.message = message
        self.status_code_of_api_response = status_code_of_api_response
        if json_content_of_api_response:
            try:
                parsed_json = json.loads(json_content_of_api_response)
                if "knora-api:error" in parsed_json:
                    knora_api_error = parsed_json["knora-api:error"]
                    knora_api_error = re.sub(r"^dsp\.errors\.[A-Za-z]+?: ?", "", knora_api_error)
                    self.original_error_message_from_api = knora_api_error
            except json.JSONDecodeError:
                pass
        self.reason_for_failure_from_api_response = reason_for_failure_from_api_response
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
