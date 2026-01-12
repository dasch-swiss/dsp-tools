from dsp_tools.error.exceptions import BaseError
from dsp_tools.setup.logger_config import LOGGER_SAVEPATH


class FatalNonOkApiResponseCode(BaseError):
    """This error is raised when the API gives an unexpected response, that we cannot anticipate and handle cleanly."""

    def __init__(self, request_url: str, status_code: int, response_text: str) -> None:
        resp_txt = response_text[:200] if len(response_text) > 200 else response_text
        msg = (
            f"We currently do not support the following API response code for this request.\n"
            f"Status code: {status_code}\n"
            f"Request URL: {request_url}\n"
            f"Original Response: {resp_txt}\n"
            f"Please contact support@dasch.swiss with the log file at {LOGGER_SAVEPATH}."
        )
        super().__init__(msg)
