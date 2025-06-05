import urllib.parse
from dataclasses import dataclass
from functools import cache, cached_property
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

    def get_list_names_and_iris_from_server(self) -> dict[str, str]:
        project_iri = quote_plus(self._proj_iri)
        params = RequestParameters("GET", f"{self.auth.server}/admin/lists?projectIri={project_iri}", timeout=10)
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout)
        log_response(response)
        lists: list[dict[str, Any]] = response.json()["lists"]
        logger.info(f"Found {len(lists)} lists for project")
        return {lst["name"]: lst["id"] for lst in lists}

    @cached_property
    def _proj_iri(self) -> str:
        params = RequestParameters("GET", f"{self.auth.server}/admin/projects/shortcode/{self.shortcode}", timeout=10)
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout)
        log_response(response)
        return cast(str, response.json()["project"]["id"])

    def create_root_node(self, node: dict[str, Any]) -> str:
        data = {
            "name": node["name"],
            "labels": [{"language": lang, "value": val} for lang, val in node["labels"].items()],
            "comments": [{"language": lang, "value": val} for lang, val in node["comments"].items()],
            "projectIri": self._proj_iri,
        }
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", f"{self.auth.server}/admin/lists", timeout=10, data=data, headers=headers)
        log_request(params)
        response = requests.post(params.url, json=params.data, timeout=params.timeout, headers=params.headers)
        log_response(response)
        return cast(str, response.json()["list"]["listinfo"]["id"])

    def create_child_node(self, node: dict[str, Any], parent_iri: str) -> str:
        data = {
            "name": node["name"],
            "labels": [{"language": lang, "value": val} for lang, val in node["labels"].items()],
            "projectIri": self._proj_iri,
            "parentNodeIri": parent_iri,
        }
        if cmt := node.get("comments"):
            data["comments"] = [{"language": lang, "value": val} for lang, val in cmt.items()]
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        url = f"{self.auth.server}/admin/lists/{urllib.parse.quote(parent_iri)}"
        params = RequestParameters("POST", url=url, timeout=10, data=data, headers=headers)
        log_request(params)
        response = requests.post(params.url, json=params.data, timeout=params.timeout, headers=params.headers)
        log_response(response)
        return cast(str, response.json()["nodeinfo"]["id"])
