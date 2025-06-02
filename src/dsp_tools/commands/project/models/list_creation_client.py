from dataclasses import dataclass
from functools import cache
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class ListCreationClient:
    auth: AuthenticationClient
    shortcode: str

    def _get_list_names_from_server(self) -> list[str]:
        project_iri = quote_plus(self._get_proj_iri())
        params = RequestParameters("GET", f"{self.auth.server}/admin/lists?projectIri={project_iri}", timeout=10)
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout)
        log_response(response)
        lists: list[dict[str, Any]] = response.json()["lists"]
        logger.info(f"Found {len(lists)} lists for project")
        return [lst["name"] for lst in lists]

    @cache
    def _get_proj_iri(self) -> str:
        params = RequestParameters("GET", f"{self.auth.server}/admin/projects/shortcode/{self.shortcode}", timeout=10)
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout)
        log_response(response)
        return cast(str, response.json()["project"]["id"])
