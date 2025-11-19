from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import requests
from loguru import logger
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class PermissionsClient:
    auth: AuthenticationClient
    proj_iri: str

    def get_project_doaps(self) -> list[dict[str, Any]]:
        params = RequestParameters(
            "GET",
            f"{self.auth.server}/admin/permissions/doap/{quote_plus(self.proj_iri)}",
            timeout=10,
            headers={"Accept": "application/json", "Authorization": f"Bearer {self.auth.get_token()}"},
        )
        log_request(params)
        try:
            response = requests.get(params.url, timeout=params.timeout, headers=params.headers)
            log_response(response)
        except RequestException:
            logger.exception("Error while retrieving existing DOAPs")
            return []
        res: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
        return res

    def delete_doap(self, doap_iri: str) -> bool:
        params = RequestParameters(
            "DELETE",
            f"{self.auth.server}/admin/permissions/{quote_plus(doap_iri)}",
            timeout=10,
            headers={"Authorization": f"Bearer {self.auth.get_token()}"},
        )
        log_request(params)
        try:
            response = requests.delete(params.url, timeout=params.timeout, headers=params.headers)
            log_response(response)
        except RequestException:
            logger.exception("Error while deleting DOAP")
            return False
        return True

    def create_new_doap(self, payload: dict[str, Any]) -> bool:
        params = RequestParameters(
            "POST",
            f"{self.auth.server}/admin/permissions/doap",
            timeout=10,
            headers={"Authorization": f"Bearer {self.auth.get_token()}"},
            data=payload,
        )
        log_request(params)
        try:
            response = requests.post(params.url, timeout=params.timeout, headers=params.headers, json=params.data)
            log_response(response)
        except RequestException:
            logger.exception("Error while creating new DOAP")
            return False
        return True
