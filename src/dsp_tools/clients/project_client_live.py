from dataclasses import dataclass
from http import HTTPStatus

import requests

from dsp_tools.clients.project_client import ProjectInfoClient
from dsp_tools.error.exceptions import UnexpectedApiResponseError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request


@dataclass
class ProjectInfoClientLive(ProjectInfoClient):
    api_url: str

    def get_project_iri(self, shortcode: str) -> str | None:
        url = f"{self.api_url}/admin/projects/shortcode/{shortcode}"
        timeout = 30
        params = RequestParameters("GET", url, timeout)
        log_request(params)
        response = requests.get(url, timeout=timeout)
        if response.ok:
            result = response.json()
            return result["project"]["id"]
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None
        raise UnexpectedApiResponseError(f"Encountered unexpected API response with the code {response.status_code}")
