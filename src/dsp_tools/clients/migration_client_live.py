from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import cast
from urllib.parse import quote

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.migration_client import ExportImportStatus
from dsp_tools.clients.migration_client import MigrationExportClient
from dsp_tools.clients.migration_client import MigrationImportClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_60 = 60

STATUS_MAPPER = {
    "in_progress": ExportImportStatus.IN_PROGRESS,
    "completed": ExportImportStatus.COMPLETED,
    "failed": ExportImportStatus.FAILED,
}


@dataclass
class MigrationExportClientLive(MigrationExportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_export(self) -> str:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, TIMEOUT_60, headers=headers)
        log_request(params)

        try:
            response = requests.post(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response)

        if response.status_code == HTTPStatus.ACCEPTED:
            return cast(str, response.json()["id"])
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("Only system admins are allowed to export a project.")
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def get_status(self, export_id: str) -> ExportImportStatus:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports/{export_id}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT_60, headers=headers)
        return _make_status_check_call(params)

    def get_download(self, export_id: str, destination: Path) -> None:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports/{export_id}/download"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT_60, headers=headers)
        log_request(params)

        try:
            response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response, include_response_content=False)

        if response.ok:
            destination.write_bytes(response.content)
            return
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("Only system admins are allowed to download a project export.")
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def delete_export(self, export_id: str) -> None:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports/{export_id}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("DELETE", url, TIMEOUT_60, headers=headers)
        _make_delete_call(params)


@dataclass
class MigrationImportClientLive(MigrationImportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_import(self, zip_path: Path) -> str:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/imports"
        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}",
            "Content-Type": "application/zip",
        }
        params = RequestParameters("POST", url, TIMEOUT_60, headers=headers)
        log_request(params)

        try:
            zip_bytes = zip_path.read_bytes()
            response = requests.post(url=params.url, headers=params.headers, data=zip_bytes, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)

        log_response(response, include_response_content=False)

        if response.status_code == HTTPStatus.ACCEPTED:
            return cast(str, response.json()["id"])
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("Only system admins are allowed to import a project.")
        raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def get_status(self, import_id: str) -> ExportImportStatus:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/imports/{import_id}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT_60, headers=headers)
        return _make_status_check_call(params)

    def delete_import(self, import_id: str) -> None:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/imports/{import_id}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("DELETE", url, TIMEOUT_60, headers=headers)
        _make_delete_call(params)


def _make_status_check_call(params: RequestParameters) -> ExportImportStatus:
    log_request(params)
    try:
        response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
    except RequestException as err:
        log_and_raise_request_exception(err)
    log_response(response)
    if response.ok:
        return STATUS_MAPPER[response.json()["status"]]
    if response.status_code == HTTPStatus.FORBIDDEN:
        raise BadCredentialsError("You don't have permission to check the status.")
    raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)


def _make_delete_call(params: RequestParameters) -> None:
    log_request(params)
    try:
        response = requests.delete(url=params.url, headers=params.headers, timeout=params.timeout)
    except RequestException as err:
        log_and_raise_request_exception(err)
    log_response(response)
    if response.status_code == HTTPStatus.NO_CONTENT:
        return
    if response.status_code == HTTPStatus.FORBIDDEN:
        raise BadCredentialsError("You don't have permission to delete the export / import id.")
    raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)
