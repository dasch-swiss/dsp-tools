from dataclasses import dataclass
from typing import Any
from typing import cast

import requests
from requests import RequestException

from dsp_tools.clients.group_user_clients import GroupClient
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_and_warn_unexpected_non_ok_response
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT = 30


@dataclass
class GroupClientLive(GroupClient):
    api_url: str

    def get_all_groups(self) -> list[dict[str, Any]]:
        url = f"{self.api_url}/admin/groups"
        params = RequestParameters("GET", url, TIMEOUT)
        log_request(params)
        try:
            response = requests.get(params.url, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            result = response.json()
            return cast(list[dict[str, Any]], result["groups"])
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return []

    def create_new_group(self, group_dict: dict[str, Any]) -> str | None:
        url = f"{self.api_url}/admin/groups"
        params = RequestParameters("POST", url, TIMEOUT, data=group_dict)
        log_request(params)
        try:
            response = requests.post(params.url, data=params.data_serialized, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)
        if response.ok:
            result = response.json()
            return cast(str, result["group"]["id"])
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None
