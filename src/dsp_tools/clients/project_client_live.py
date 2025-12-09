from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.project_client import ProjectClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from dsp_tools.error.exceptions import ProjectNotFoundError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class ProjectClientLive(ProjectClient):
    server: str
    auth: AuthenticationClient

    def get_project_iri(self, shortcode: str) -> str:
        url = f"{self.server}/admin/projects/shortcode/{shortcode}"
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
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ProjectNotFoundError(f"The project with the shortcode {shortcode} does not exist on this server. ")
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def post_new_project(self, project_info: dict[str, Any]) -> str | ResponseCodeAndText:
        url = f"{self.server}/admin/projects"
        timeout = 10
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, timeout, headers=headers, data=project_info)
        log_request(params)
        try:
            response = requests.post(
                params.url, timeout=params.timeout, headers=params.headers, data=params.data_serialized
            )
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response)
        if response.ok:
            result = response.json()
            return cast(str, result["project"]["id"])
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError(
                "Only a SystemAdmin can create a project, your permissions are insufficient for this action. "
                "Please contact support@dasch.swiss if you require a new project."
            )
        return ResponseCodeAndText(response.status_code, response.text)
