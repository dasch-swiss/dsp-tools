from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_vre_lib.clients.authentication_client import AuthenticationClient
from dsp_vre_lib.clients.request_utils import ResponseCodeAndText


@dataclass
class ValueClient(Protocol):
    server: str
    auth: AuthenticationClient

    def post_new_value(self, value_json: dict[str, Any]) -> ResponseCodeAndText | None:
        """
        POST a JSON-LD resource payload to /v2/values.
        """

    def replace_existing_value(self, value_json: dict[str, Any]) -> ResponseCodeAndText | None:
        """
        PUT a JSON-LD resource payload to /v2/values.
        """
