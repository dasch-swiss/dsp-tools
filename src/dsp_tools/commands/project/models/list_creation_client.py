from dataclasses import dataclass
from typing import Any
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

    def _get_list_names_from_server(self, project_iri: str) -> list[str]:
        params = RequestParameters(
            "GET", f"{self.auth.server}/admin/lists?projectIri={quote_plus(project_iri)}", timeout=10
        )
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout)
        log_response(response)
        lists: list[dict[str, Any]] = response.json()["lists"]
        logger.info(f"Found {len(lists)} lists for project")
        return [lst["name"] for lst in lists]
