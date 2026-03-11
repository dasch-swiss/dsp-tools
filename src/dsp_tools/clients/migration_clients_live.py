from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Literal
from typing import cast
from urllib.parse import quote

import requests
from requests import RequestException

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.exceptions import MigrationExportExistsError
from dsp_tools.clients.exceptions import MigrationExportImportInProgressError
from dsp_tools.clients.exceptions import MigrationImportExistsError
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients import MigrationImportClient
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_request_exception
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response

TIMEOUT_60 = 60

TIMEOUT_ZIP_ENDPOINT = 60 * 120

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

    def post_export(self, skip_assets: bool = False) -> ExportId:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports?skipAssets={skip_assets}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("POST", url, TIMEOUT_60, headers=headers)
        log_request(params)

        try:
            response = requests.post(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)

        match response.status_code:
            case HTTPStatus.ACCEPTED:
                return ExportId(cast(str, response.json()["id"]))
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("Only system admins are allowed to export a project.")
            case HTTPStatus.CONFLICT:
                raise MigrationExportExistsError()
            case _:
                raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def get_status(self, export_id: ExportId) -> ExportImportStatus:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports/{export_id.id_}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT_60, headers=headers)
        return _make_status_check_call(params)

    def get_download(self, export_id: ExportId, destination: Path) -> None:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports/{export_id.id_}/download"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT_ZIP_ENDPOINT, headers=headers)
        log_request(params)

        try:
            response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response, include_response_content=False)

        match response.status_code:
            case HTTPStatus.OK:
                destination.write_bytes(response.content)
                return
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("Only system admins are allowed to download a project export.")
            case HTTPStatus.CONFLICT:
                raise MigrationExportImportInProgressError(
                    "It is not permissible to download a project at the same time."
                )
            case _:
                raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def delete_export(self, export_id: ExportId) -> None:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/exports/{export_id.id_}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("DELETE", url, TIMEOUT_60, headers=headers)
        _make_delete_call(params, "export")


@dataclass
class MigrationImportClientLive(MigrationImportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_import(self, zip_path: Path) -> ImportId:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/imports"
        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}",
            "Content-Type": "application/zip",
        }
        params = RequestParameters("POST", url, TIMEOUT_ZIP_ENDPOINT, headers=headers)
        log_request(params)

        try:
            with open(zip_path, "rb") as binary_io:
                response = requests.post(
                    url=params.url,
                    headers=params.headers,
                    data=binary_io,
                    timeout=params.timeout,
                )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response)

        match response.status_code:
            case HTTPStatus.ACCEPTED:
                return ImportId(cast(str, response.json()["id"]))
            case HTTPStatus.FORBIDDEN:
                raise BadCredentialsError("Only system admins are allowed to import a project.")
            case HTTPStatus.CONFLICT:
                raise MigrationImportExistsError()
            case _:
                raise FatalNonOkApiResponseCode(url, response.status_code, response.text)

    def get_status(self, import_id: ImportId) -> ExportImportStatus:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/imports/{import_id.id_}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("GET", url, TIMEOUT_60, headers=headers)
        return _make_status_check_call(params)

    def delete_import(self, import_id: ImportId) -> None:
        encoded_iri = quote(self.project_iri, safe="")
        url = f"{self.server}/v3/projects/{encoded_iri}/imports/{import_id.id_}"
        headers = {"Authorization": f"Bearer {self.auth.get_token()}"}
        params = RequestParameters("DELETE", url, TIMEOUT_60, headers=headers)
        _make_delete_call(params, "import")


def _make_status_check_call(params: RequestParameters) -> ExportImportStatus:
    log_request(params)
    try:
        response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
    except RequestException as err:
        log_and_raise_request_exception(err)
    log_response(response)

    match response.status_code:
        case HTTPStatus.OK:
            return STATUS_MAPPER[response.json()["status"]]
        case HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You don't have permission to check the status.")
        case _:
            raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)


def _make_delete_call(params: RequestParameters, process: Literal["import", "export"]) -> None:
    log_request(params)
    try:
        response = requests.delete(url=params.url, headers=params.headers, timeout=params.timeout)
    except RequestException as err:
        log_and_raise_request_exception(err)
    log_response(response)

    match response.status_code:
        case HTTPStatus.NO_CONTENT:
            return
        case HTTPStatus.NOT_FOUND:
            # This means that the ID does not exist on the server.
            # This is possible for example if the export / import was done both on localhost with a restart in-between.
            return
        case HTTPStatus.FORBIDDEN:
            raise BadCredentialsError("You don't have permission to delete the export / import id.")
        case HTTPStatus.CONFLICT:
            raise MigrationExportImportInProgressError(f"It is not permissible to delete the {process} at this point.")
        case _:
            raise FatalNonOkApiResponseCode(params.url, response.status_code, response.text)
