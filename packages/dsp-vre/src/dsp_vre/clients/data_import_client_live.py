from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any
from typing import Never
from typing import cast
from urllib.parse import quote
from urllib.parse import quote_plus

import requests
from requests import RequestException
from requests import Response

from dsp_vre.clients.authentication_client import AuthenticationClient
from dsp_vre.clients.data_import_client import DataImportClient
from dsp_vre.clients.data_import_client import DataImportId
from dsp_vre.clients.data_import_client import DataImportStatus
from dsp_vre.clients.data_import_client import DataImportStatusValue
from dsp_vre.clients.exceptions import BadCredentialsError
from dsp_vre.clients.exceptions import DataImportExistsError
from dsp_vre.clients.exceptions import DataImportInProgressError
from dsp_vre.clients.exceptions import DataImportNotEnabledError
from dsp_vre.clients.exceptions import DataImportNotFoundError
from dsp_vre.clients.exceptions import DataImportPayloadTooLargeError
from dsp_vre.clients.exceptions import DataImportPreconditionError
from dsp_vre.clients.exceptions import DataImportRunningError
from dsp_vre.clients.exceptions import DspVreUserError
from dsp_vre.clients.exceptions import FatalNonOkApiResponseCodeError
from dsp_vre.clients.exceptions import OnBehalfOfUserIneligibleError
from dsp_vre.clients.exceptions import OnBehalfOfUserNotFoundError
from dsp_vre.clients.exceptions import ProjectNotFoundError
from dsp_vre.clients.request_utils import USER_AGENT
from dsp_vre.clients.request_utils import ApiV3ErrorDetails
from dsp_vre.clients.request_utils import RequestParameters
from dsp_vre.clients.request_utils import log_and_raise_request_exception
from dsp_vre.clients.request_utils import log_request
from dsp_vre.clients.request_utils import log_response
from dsp_vre.clients.request_utils import parse_api_v3_error

TIMEOUT_60 = 60

# The server saves the whole payload before it answers.
TIMEOUT_7200 = 60 * 120


@dataclass
class DataImportClientLive(DataImportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_import(self, payload_path: Path, on_behalf_of_user: str) -> DataImportId:
        headers = self._headers() | {"Content-Type": "application/ld+json"}
        # The query is built into the URL so that log_request logs the encoded URL that is sent.
        url = f"{self._base_url()}?onBehalfOfUser={quote_plus(on_behalf_of_user)}"
        params = RequestParameters("POST", url, TIMEOUT_7200, headers=headers)
        log_request(params)
        try:
            # requests streams a file object and sets the Content-Length from the file size.
            with open(payload_path, "rb") as payload:
                response = requests.post(
                    url=params.url,
                    headers=params.headers,
                    data=payload,
                    timeout=params.timeout,
                )
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response, status_code=response.status_code)
        if response.status_code == HTTPStatus.ACCEPTED:
            return DataImportId(cast(str, response.json()["id"]))
        _raise_for_data_import_error(response, params.url)

    def get_status(self, import_id: DataImportId) -> DataImportStatus:
        params = RequestParameters("GET", self._import_url(import_id), TIMEOUT_60, headers=self._headers())
        log_request(params)
        try:
            response = requests.get(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response, status_code=response.status_code)
        if response.status_code == HTTPStatus.OK:
            return _parse_status(response, params.url)
        _raise_for_data_import_error(response, params.url)

    def delete_import(self, import_id: DataImportId) -> None:
        params = RequestParameters("DELETE", self._import_url(import_id), TIMEOUT_60, headers=self._headers())
        log_request(params)
        try:
            response = requests.delete(url=params.url, headers=params.headers, timeout=params.timeout)
        except RequestException as err:
            log_and_raise_request_exception(err)
        log_response(response, status_code=response.status_code)
        if response.status_code == HTTPStatus.NO_CONTENT:
            return
        _raise_for_data_import_error(response, params.url)

    def _base_url(self) -> str:
        return f"{self.server}/v3/projects/{quote(self.project_iri, safe='')}/data-imports"

    def _import_url(self, import_id: DataImportId) -> str:
        return f"{self._base_url()}/{quote(import_id.id, safe='')}"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.auth.get_token()}", "DSP-Client": USER_AGENT}


def _parse_status(response: Response, url: str) -> DataImportStatus:
    body: dict[str, Any] = response.json()
    try:
        status = DataImportStatusValue(body["status"])
    except ValueError:
        raise FatalNonOkApiResponseCodeError(url, response.status_code, response.text) from None
    return DataImportStatus(
        id=DataImportId(cast(str, body["id"])),
        project_iri=cast(str, body["projectIri"]),
        status=status,
        error_message=cast(str | None, body.get("errorMessage")),
    )


def _raise_for_data_import_error(response: Response, url: str) -> Never:
    if response.status_code == HTTPStatus.FORBIDDEN:
        raise BadCredentialsError("Only system admins can run a bulk data import.")
    v3_errors = parse_api_v3_error(response).v3_errors
    error = v3_errors[0] if v3_errors else None
    if response.status_code == HTTPStatus.REQUEST_ENTITY_TOO_LARGE:
        raise _payload_too_large(error)
    if error is None:
        raise FatalNonOkApiResponseCodeError(url, response.status_code, response.text)
    raise _error_from_code(error) or FatalNonOkApiResponseCodeError(url, response.status_code, response.text)


def _payload_too_large(error: ApiV3ErrorDetails | None) -> DataImportPayloadTooLargeError:
    if error is None:
        # A chunked body above the 1 MiB server cap gets a bare 413 without a v3 error body.
        msg = "The server rejected the payload because it is too large."
        return DataImportPayloadTooLargeError(size=None, max_size=None, message=msg)
    size, max_size = error.details.get("size"), error.details.get("max")
    return DataImportPayloadTooLargeError(
        size=int(size) if size is not None else None,
        max_size=int(max_size) if max_size is not None else None,
        message=error.message,
    )


def _error_from_code(error: ApiV3ErrorDetails) -> DspVreUserError | None:  # noqa: PLR0911 (Too many return statements)
    details = error.details
    match error.error_code:
        case "feature_missing":
            return DataImportNotEnabledError(error.message)
        case "project_not_found":
            return ProjectNotFoundError(error.message)
        case "on_behalf_of_user_not_found":
            return OnBehalfOfUserNotFoundError(details.get("id", ""), error.message)
        case "on_behalf_of_user_ineligible":
            return OnBehalfOfUserIneligibleError(details.get("id", ""), details.get("reason", ""), error.message)
        case "project_ontologies_missing" | "data_graph_exists" as code:
            return DataImportPreconditionError(code, error.message)
        case "import_running":
            return DataImportRunningError(error.message)
        case "import_exists":
            return DataImportExistsError(details.get("id", ""), details.get("projectIri", ""), error.message)
        case "import_not_found":
            return DataImportNotFoundError(details.get("id", ""), error.message)
        case "import_in_progress":
            return DataImportInProgressError(details.get("id", ""), error.message)
        case _:
            return None
