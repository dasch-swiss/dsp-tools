from typing import Any

from requests import Response

from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.legal_info_client import LegalInfoClient


class LegalInfoClientLive(LegalInfoClient):
    server: str
    project_shortcode: str
    authentication_client: AuthenticationClientLive

    def post_copyright_holders(self, copyright_holders: list[str]) -> None:
        """Send a list of new copyright holders to the API"""

    def _send_request(self, route: str, payload: list[str], headers: dict[str, Any]) -> Response:
        pass
