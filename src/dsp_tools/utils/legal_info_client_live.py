import json
from dataclasses import dataclass

import requests
from requests import ReadTimeout
from requests import Response

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.legal_info_client import LegalInfoClient
from dsp_tools.utils.request_utils import GenericRequestParameters
from dsp_tools.utils.request_utils import log_and_raise_timeouts
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response
from dsp_tools.utils.set_encoder import SetEncoder

TIMEOUT = 60

HTTP_INSUFFICIENT_CREDENTIALS = 403


@dataclass
class LegalInfoClientLive(LegalInfoClient):
    server: str
    project_shortcode: str
    authentication_client: AuthenticationClientLive

    def post_copyright_holders(self, copyright_holders: list[str]) -> None:
        """Send a list of new copyright holders to the API"""
        # The maximum allowed number of data elements is 100,
        # this segments the entries so that it does not go over the limit.
        segmented_data = _segment_data(copyright_holders)
        for seg in segmented_data:
            try:
                response = self._post_and_log_request("copyright-holders", seg)
            except (TimeoutError, ReadTimeout) as err:
                log_and_raise_timeouts(err)
            if response.ok:
                continue
            if response.status_code == HTTP_INSUFFICIENT_CREDENTIALS:
                raise BadCredentialsError(
                    "Only a project or system administrator can create new copyright holders. "
                    "Your permissions are insufficient for this action."
                )
            else:
                raise BaseError(
                    f"An unexpected response with the status code {response.status_code} from the API occurred. "
                    f"Please consult warnings.log for details."
                )

    def _post_and_log_request(self, endpoint: str, data: list[str]) -> Response:
        url = f"{self.server}/admin/projects/shortcode/{self.project_shortcode}/legal-info/{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
        }
        params = GenericRequestParameters("POST", url, TIMEOUT, data, headers)
        log_request(params)
        data_dict = {"data": data}
        encoded_data = json.dumps(data_dict, cls=SetEncoder, ensure_ascii=False).encode("utf-8")
        response = requests.post(url=url, headers=headers, data=encoded_data, timeout=TIMEOUT)
        log_response(response)
        return response


def _segment_data(data: list[str]) -> list[list[str]]:
    segmented = []
    while len(data) > 100:
        segmented.append(data[:100])
        data = data[100:]

    segmented.append(data)
    return segmented
