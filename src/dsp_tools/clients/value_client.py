from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import ResponseCodeAndText


class ValueClient(Protocol):
    server: str
    auth: AuthenticationClient

    def post_new_value(self, value_json: dict[str, Any]) -> None | ResponseCodeAndText:
        """
        POST a JSON-LD resource payload to /v2/values.
        """

    def replace_existing_value(self, value_json: dict[str, Any]) -> None | ResponseCodeAndText:
        """
        PUT a JSON-LD resource payload to /v2/values.
        """
