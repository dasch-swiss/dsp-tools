from dataclasses import dataclass

import requests
from loguru import logger
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.metadata_client import ExistingResourcesRetrieved
from dsp_tools.clients.metadata_client import MetadataClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_warn_unexpected_non_ok_response
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 120


@dataclass
class MetadataClientLive(MetadataClient):
    server: str
    authentication_client: AuthenticationClient

    def get_resource_metadata(self, shortcode: str) -> tuple[ExistingResourcesRetrieved, list[dict[str, str]]]:
        url = f"{self.server}/v2/metadata/projects/{shortcode}/resources?format=JSON"
        header = {"Authorization": f"Bearer {self.authentication_client.get_token()}"}
        params = RequestParameters(method="GET", url=url, timeout=TIMEOUT, headers=header)
        logger.debug("GET Resource Metadata")
        log_request(params)
        try:
            response = requests.get(
                url=params.url,
                headers=params.headers,
                timeout=params.timeout,
            )
        except RequestException as err:
            logger.error(err)
            return ExistingResourcesRetrieved.FALSE, []
        if response.ok:
            log_response(response, include_response_content=False)
            logger.debug(f"{len(response.json())} NUMBER OF RESOURCES RETRIEVED")
            return ExistingResourcesRetrieved.TRUE, response.json()
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return ExistingResourcesRetrieved.FALSE, []
