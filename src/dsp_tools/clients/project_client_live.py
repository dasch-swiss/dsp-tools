from dataclasses import dataclass
from typing import cast

import requests
from requests import RequestException

from dsp_tools.clients.project_client import ProjectInfoClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class ProjectInfoClientLive(ProjectInfoClient):
    api_url: str

    def get_project_iri(self, shortcode: str) -> str | None:
        url = f"{self.api_url}/admin/projects/shortcode/{shortcode}"
        timeout = 30
        params = RequestParameters("GET", url, timeout)
        log_request(params)
        try:
            response = requests.get(url, timeout=timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response)
        if response.ok:
            result = response.json()
            return cast(str, result["project"]["id"])
        return None
