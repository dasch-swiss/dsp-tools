from dataclasses import dataclass

import requests
from requests import ReadTimeout
from requests import Response

from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.legal_info_client import LegalInfoClient
from dsp_tools.utils.request_utils import GenericRequestParameters
from dsp_tools.utils.request_utils import log_and_raise_timeouts
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 60


@dataclass
class LegalInfoClientLive(LegalInfoClient):
    server: str
    project_shortcode: str
    authentication_client: AuthenticationClientLive

    def __post_init__(self) -> None:
        if not self.server.endswith("/"):
            self.server = f"{self.server}/"

    def post_copyright_holders(self, copyright_holders: list[str]) -> None:
        """Send a list of new copyright holders to the API"""
        # The maximum allowed number of data elements is 100,
        # this segments the entries so that it does not go over the limit.
        segmented_data = _segment_data(copyright_holders)
        for seg in segmented_data:
            try:
                self._post_request("copyright-holders", seg)
            except TimeoutError | ReadTimeout as err:
                log_and_raise_timeouts(err)

    def _post_request(self, endpoint: str, data: list[str]) -> Response:
        url = f"{self.server}admin/projects/shortcode/{self.project_shortcode}/legal-info/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        payload = {"data": [item.encode("utf-8") for item in data]}
        params = GenericRequestParameters("POST", url, TIMEOUT, payload, headers)
        log_request(params)
        response = requests.post(url=url, headers=headers, data=payload, timeout=TIMEOUT)
        log_response(response)
        return response


def _segment_data(data: list[str]) -> list[list[str]]:
    segmented = []
    while len(data) > 100:
        segmented.append(data[:100])
        data = data[100:]

    segmented.append(data)
    return segmented
