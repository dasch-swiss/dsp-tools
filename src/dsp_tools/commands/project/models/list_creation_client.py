import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import requests
from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient


@dataclass
class ListCreationClient:
    auth: AuthenticationClient

    
    def _get_list_names_from_server(self, project_iri: str) -> list[str]:
        iri = quote_plus(project_iri)
        url = f"{self.auth.server}/admin/lists?projectIri={iri}"
        logger.debug(f"REQUEST: {json.dumps({'method': 'GET', 'url': url})}")
        response = requests.get(url, timeout=10)
        logger.debug(f"RESPONSE {response.status_code}: {response.text}")
        lists: list[dict[str, Any]] = response.json()["lists"]
        logger.info(f"Found {len(lists)} lists for project")
        return [lst["name"] for lst in lists]
