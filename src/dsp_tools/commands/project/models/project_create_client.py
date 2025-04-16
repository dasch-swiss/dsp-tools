import json
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any

import requests
from loguru import logger

from dsp_tools.utils.authentication_client import AuthenticationClient


@dataclass
class ProjectCreateClient:
    auth: AuthenticationClient

    def get_existing_shortcodes_and_shortnames(self) -> tuple[set[str], set[str]]:
        url = f"{self.auth.server}/admin/projects"
        headers = {
            "User-Agent": f"DSP-TOOLS/{version('dsp-tools')}",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }
        logger.debug(f"REQUEST: GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        logger.debug(f"RESPONSE {response.status_code}: {response.text}")
        res_json: dict[str, Any] = response.json()
        shortcodes = [x.get("shortcode") for x in res_json["projects"]]
        shortnames = [x.get("shortname") for x in res_json["projects"]]
        return {x for x in shortcodes if x}, {x for x in shortnames if x}

    def create_project(self, payload: dict[str, Any]) -> bool:
        url = f"{self.auth.server}/admin/projects"
        headers = {
            "User-Agent": f"DSP-TOOLS/{version('dsp-tools')}",
            "Authorization": f"Bearer {self.auth.get_token()}",
            "Content-Type": "application/json",
        }
        logger.debug(f"REQUEST: {json.dumps({'method': 'POST', 'url': url, 'payload': payload})}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        logger.debug(f"RESPONSE {response.status_code}: {response.text}")
        return response.ok
