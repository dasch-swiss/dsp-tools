from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

import requests

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class ProjectClient:
    auth: AuthenticationClient

    def get_existing_shortcodes_and_shortnames(self) -> tuple[set[str], set[str]]:
        params = RequestParameters(
            "GET",
            f"{self.auth.server}/admin/projects",
            timeout=10,
            headers={
                "User-Agent": f"DSP-TOOLS/{version('dsp-tools')}",
                "Authorization": f"Bearer {self.auth.get_token()}",
            },
        )
        log_request(params)
        response = requests.get(params.url, headers=params.headers, timeout=params.timeout)
        log_response(response)
        res_json: dict[str, Any] = response.json()
        shortcodes = [x.get("shortcode") for x in res_json["projects"]]
        shortnames = [x.get("shortname") for x in res_json["projects"]]
        return {x for x in shortcodes if x}, {x for x in shortnames if x}

    def create_project(self, payload: dict[str, Any]) -> bool:
        params = RequestParameters(
            "POST",
            f"{self.auth.server}/admin/projects",
            data=payload,
            headers={
                "User-Agent": f"DSP-TOOLS/{version('dsp-tools')}",
                "Authorization": f"Bearer {self.auth.get_token()}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        log_request(params)
        response = requests.post(params.url, headers=params.headers, json=params.data, timeout=params.timeout)
        log_response(response)
        return response.ok
