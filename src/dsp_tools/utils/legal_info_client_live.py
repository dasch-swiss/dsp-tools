from dataclasses import dataclass

import requests
from requests import Response

from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.legal_info_client import LegalInfoClient


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

    def _post_request(self, endpoint: str, data: list[str]) -> Response:
        url = f"{self.server}admin/projects/shortcode/{self.project_shortcode}/legal-info/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        payload = {"data": data}
        return requests.post(url=url, headers=headers, data=payload)


def _segment_data(data: list[str]) -> list[list[str]]:
    segmented = [data[:100]]
    counter = 2

    def get_range(counter_num: int) -> tuple[int, int]:
        start = counter_num * 100
        end = (counter_num + 1) * 100
        return start, end

    while len(data) > 100:
        start_range, end_range = get_range(counter)
        segmented.append(data[start_range:end_range])
        counter += 1
    start_range, end_range = get_range(counter + 1)
    segmented.append(data[start_range:end_range])
    return segmented
