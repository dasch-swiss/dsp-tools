from dataclasses import dataclass
from functools import cached_property
from typing import Any
from typing import cast

import requests

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class GroupClient:
    auth: AuthenticationClient
    shortcode: str

    def get_project_groups_from_server(self) -> dict[str, str]:
        """Get all groups of a given project from the server, in the form `{name : iri}`"""
        params = RequestParameters(
            "GET", f"{self.auth.server}/admin/groups", timeout=10, headers={"Accept": "application/json"}
        )
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout, headers=params.headers)
        log_response(response)
        all_groups: list[dict[str, Any]] = response.json()["groups"]
        proj_groups = filter(lambda a: a["project"]["shortcode"] == self.shortcode, all_groups)
        return {grp["name"]: grp["id"] for grp in proj_groups}

    def create_group(self, group: dict[str, Any]) -> str:
        """Create a group on a DSP server and return its IRI"""
        data = {
            "name": group["name"],
            "projectIri": self._proj_iri,
            "descriptions": [{"value": val, "language": lang} for lang, val in group["descriptions"].items()],
        }
        if "status" in group:
            data["status"] = group["status"]
        if "selfjoin" in group:
            data["selfjoin"] = group["selfjoin"]
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", f"{self.auth.server}/admin/groups", timeout=10, data=data, headers=headers)
        log_request(params)
        response = requests.post(params.url, timeout=params.timeout, headers=params.headers)
        log_response(response)
        return cast(str, response.json()["group"]["id"])

    @cached_property
    def _proj_iri(self) -> str:
        params = RequestParameters("GET", f"{self.auth.server}/admin/projects/shortcode/{self.shortcode}", timeout=10)
        log_request(params)
        response = requests.get(params.url, timeout=params.timeout)
        log_response(response)
        return cast(str, response.json()["project"]["id"])
