from dataclasses import dataclass

import requests
from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.metadata_client import MetadataClient
from dsp_tools.clients.metadata_client import MetadataResponse
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 120


@dataclass
class MetadataClientLive(MetadataClient):
    server: str
    authentication_client: AuthenticationClient

    def get_resource_metadata(self, shortcode: str) -> tuple[MetadataResponse, list[dict[str, str]]]:
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
            log_response(response, include_response_content=False)
            if response.ok:
                return MetadataResponse.METADATA_RETRIVAL_OK, response.json()
            return MetadataResponse.METADATA_RETRIVAL_NON_OK, []
        except Exception as err:  # noqa: BLE001 (blind exception)
            logger.error(err)
            return MetadataResponse.METADATA_RETRIVAL_ERROR, []
