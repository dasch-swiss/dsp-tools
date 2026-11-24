from http import HTTPStatus
from pathlib import Path
from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import JSONDecodeError
from requests import RequestException

from dsp_vre_lib.clients import AuthenticationClient
from dsp_vre_lib.clients import DataImportId
from dsp_vre_lib.clients import DataImportStatus
from dsp_vre_lib.clients import DataImportStatusValue
from dsp_vre_lib.clients.data_import_client_live import TIMEOUT_7200
from dsp_vre_lib.clients.data_import_client_live import DataImportClientLive
from dsp_vre_lib.clients.exceptions import BadCredentialsError
from dsp_vre_lib.clients.exceptions import DataImportExistsError
from dsp_vre_lib.clients.exceptions import DataImportInProgressError
from dsp_vre_lib.clients.exceptions import DataImportNotEnabledError
from dsp_vre_lib.clients.exceptions import DataImportNotFoundError
from dsp_vre_lib.clients.exceptions import DataImportPayloadTooLargeError
from dsp_vre_lib.clients.exceptions import DataImportPreconditionError
from dsp_vre_lib.clients.exceptions import DataImportRunningError
from dsp_vre_lib.clients.exceptions import DspApiRequestError
from dsp_vre_lib.clients.exceptions import FatalNonOkApiResponseCodeError
from dsp_vre_lib.clients.exceptions import OnBehalfOfUserIneligibleError
from dsp_vre_lib.clients.exceptions import OnBehalfOfUserNotFoundError
from dsp_vre_lib.clients.exceptions import ProjectNotFoundError
from dsp_vre_lib.clients.request_utils import USER_AGENT

MODULE = "dsp_vre_lib.clients.data_import_client_live"
PROJECT_IRI = "http://rdfh.ch/projects/0001"
BASE_URL = "http://0.0.0.0:3333/v3/projects/http%3A%2F%2Frdfh.ch%2Fprojects%2F0001/data-imports"
IMPORT_ID = DataImportId("import-123")


@pytest.fixture
def client() -> DataImportClientLive:
    auth = Mock(spec=AuthenticationClient)
    auth.get_token.return_value = "test-token-123"
    return DataImportClientLive(server="http://0.0.0.0:3333", project_iri=PROJECT_IRI, auth=auth)


@pytest.fixture
def payload_path(tmp_path: Path) -> Path:
    path = tmp_path / "payload.jsonld"
    path.write_text('{"@graph": []}')
    return path


def _response(status_code: int, body: Any = None, text: str = "") -> Mock:
    response = Mock(status_code=status_code, headers={}, text=text)
    if body is None:
        response.json.side_effect = JSONDecodeError("no JSON body", "", 0)
    else:
        response.json.return_value = body
    return response


def _v3_error(code: str, details: dict[str, str], message: str = "server message") -> dict[str, Any]:
    return {"message": message, "errors": [{"code": code, "message": message, "details": details}]}


def _status_body(status: str, error_message: str | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "import-123",
        "projectIri": PROJECT_IRI,
        "status": status,
        "createdBy": "http://rdfh.ch/users/root",
        "createdAt": "2026-11-24T10:00:00Z",
    }
    if error_message is not None:
        body["errorMessage"] = error_message
    return body


class TestPostImport:
    def test_accepted_returns_import_id(self, client: DataImportClientLive, payload_path: Path) -> None:
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.ACCEPTED, _status_body("in_progress"))):
            result = client.post_import(payload_path, "user@example.org")
        assert result == IMPORT_ID

    def test_request_url_encodes_on_behalf_of_user(self, client: DataImportClientLive, payload_path: Path) -> None:
        response = _response(HTTPStatus.ACCEPTED, _status_body("in_progress"))
        with patch(f"{MODULE}.requests.post", return_value=response) as mock_post:
            client.post_import(payload_path, "first+last@example.org")
        assert mock_post.call_args.kwargs["url"] == f"{BASE_URL}?onBehalfOfUser=first%2Blast%40example.org"
        assert mock_post.call_args.kwargs["timeout"] == TIMEOUT_7200

    def test_request_headers(self, client: DataImportClientLive, payload_path: Path) -> None:
        response = _response(HTTPStatus.ACCEPTED, _status_body("in_progress"))
        with patch(f"{MODULE}.requests.post", return_value=response) as mock_post:
            client.post_import(payload_path, "user@example.org")
        headers = mock_post.call_args.kwargs["headers"]
        assert headers["Content-Type"] == "application/ld+json"
        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["DSP-Client"] == USER_AGENT

    def test_body_is_a_file_object(self, client: DataImportClientLive, payload_path: Path) -> None:
        response = _response(HTTPStatus.ACCEPTED, _status_body("in_progress"))
        with patch(f"{MODULE}.requests.post", return_value=response) as mock_post:
            client.post_import(payload_path, "user@example.org")
        body = mock_post.call_args.kwargs["data"]
        assert not isinstance(body, bytes)
        assert body.name == str(payload_path)
        assert body.mode == "rb"


class TestGetStatus:
    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            ("in_progress", DataImportStatusValue.IN_PROGRESS),
            ("completed", DataImportStatusValue.COMPLETED),
        ],
    )
    def test_status_without_error_message(
        self, client: DataImportClientLive, status: str, expected: DataImportStatusValue
    ) -> None:
        response = _response(HTTPStatus.OK, _status_body(status))
        with patch(f"{MODULE}.requests.get", return_value=response) as mock_get:
            result = client.get_status(IMPORT_ID)
        assert result == DataImportStatus(IMPORT_ID, PROJECT_IRI, expected, None)
        assert mock_get.call_args.kwargs["url"] == f"{BASE_URL}/import-123"
        assert mock_get.call_args.kwargs["headers"]["DSP-Client"] == USER_AGENT

    def test_failed_status_has_error_message(self, client: DataImportClientLive) -> None:
        response = _response(HTTPStatus.OK, _status_body("failed", "Validation failed."))
        with patch(f"{MODULE}.requests.get", return_value=response):
            result = client.get_status(IMPORT_ID)
        assert result == DataImportStatus(IMPORT_ID, PROJECT_IRI, DataImportStatusValue.FAILED, "Validation failed.")

    def test_failed_status_without_error_message(self, client: DataImportClientLive) -> None:
        with patch(f"{MODULE}.requests.get", return_value=_response(HTTPStatus.OK, _status_body("failed"))):
            result = client.get_status(IMPORT_ID)
        assert result.error_message is None

    def test_unknown_status_value(self, client: DataImportClientLive) -> None:
        with patch(f"{MODULE}.requests.get", return_value=_response(HTTPStatus.OK, _status_body("paused"))):
            with pytest.raises(FatalNonOkApiResponseCodeError):
                client.get_status(IMPORT_ID)

    def test_import_id_is_encoded_in_the_path(self, client: DataImportClientLive) -> None:
        response = _response(HTTPStatus.OK, _status_body("completed"))
        with patch(f"{MODULE}.requests.get", return_value=response) as mock_get:
            client.get_status(DataImportId("../exports"))
        assert mock_get.call_args.kwargs["url"] == f"{BASE_URL}/..%2Fexports"


class TestDeleteImport:
    def test_no_content_returns_none(self, client: DataImportClientLive) -> None:
        with patch(f"{MODULE}.requests.delete", return_value=_response(HTTPStatus.NO_CONTENT)) as mock_delete:
            client.delete_import(IMPORT_ID)
        assert mock_delete.call_args.kwargs["url"] == f"{BASE_URL}/import-123"
        assert mock_delete.call_args.kwargs["headers"]["DSP-Client"] == USER_AGENT


class TestErrorMapping:
    @pytest.mark.parametrize(
        ("status_code", "body", "expected_error"),
        [
            (HTTPStatus.FORBIDDEN, None, BadCredentialsError),
            (HTTPStatus.NOT_FOUND, _v3_error("feature_missing", {"name": "x"}), DataImportNotEnabledError),
            (HTTPStatus.NOT_FOUND, _v3_error("project_not_found", {"id": PROJECT_IRI}), ProjectNotFoundError),
            (
                HTTPStatus.CONFLICT,
                _v3_error("project_ontologies_missing", {"projectIri": PROJECT_IRI}),
                DataImportPreconditionError,
            ),
            (
                HTTPStatus.CONFLICT,
                _v3_error("data_graph_exists", {"projectIri": PROJECT_IRI}),
                DataImportPreconditionError,
            ),
            (HTTPStatus.CONFLICT, _v3_error("import_running", {}), DataImportRunningError),
            (HTTPStatus.CONFLICT, _v3_error("unknown_code", {}), FatalNonOkApiResponseCodeError),
            (HTTPStatus.INTERNAL_SERVER_ERROR, None, FatalNonOkApiResponseCodeError),
        ],
    )
    def test_post_error_types(
        self,
        client: DataImportClientLive,
        payload_path: Path,
        status_code: int,
        body: dict[str, Any] | None,
        expected_error: type[Exception],
    ) -> None:
        with patch(f"{MODULE}.requests.post", return_value=_response(status_code, body)):
            with pytest.raises(expected_error):
                client.post_import(payload_path, "user@example.org")

    def test_precondition_error_has_code(self, client: DataImportClientLive, payload_path: Path) -> None:
        body = _v3_error("data_graph_exists", {"projectIri": PROJECT_IRI}, "The data graph exists.")
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.CONFLICT, body)):
            with pytest.raises(DataImportPreconditionError) as exc_info:
                client.post_import(payload_path, "user@example.org")
        assert exc_info.value.error_code == "data_graph_exists"
        assert exc_info.value.message == "The data graph exists."

    def test_on_behalf_of_user_not_found(self, client: DataImportClientLive, payload_path: Path) -> None:
        body = _v3_error("on_behalf_of_user_not_found", {"id": "nobody", "projectIri": PROJECT_IRI})
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.NOT_FOUND, body)):
            with pytest.raises(OnBehalfOfUserNotFoundError) as exc_info:
                client.post_import(payload_path, "nobody")
        assert exc_info.value.user == "nobody"

    def test_on_behalf_of_user_ineligible(self, client: DataImportClientLive, payload_path: Path) -> None:
        details = {"id": "root", "projectIri": PROJECT_IRI, "reason": "is_system_admin"}
        body = _v3_error("on_behalf_of_user_ineligible", details)
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.BAD_REQUEST, body)):
            with pytest.raises(OnBehalfOfUserIneligibleError) as exc_info:
                client.post_import(payload_path, "root")
        assert exc_info.value.user == "root"
        assert exc_info.value.reason == "is_system_admin"

    def test_payload_too_large(self, client: DataImportClientLive, payload_path: Path) -> None:
        body = _v3_error("payload_too_large", {"size": "262144001", "max": "262144000"})
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, body)):
            with pytest.raises(DataImportPayloadTooLargeError) as exc_info:
                client.post_import(payload_path, "user@example.org")
        assert exc_info.value.size == 262144001
        assert exc_info.value.max_size == 262144000

    def test_payload_too_large_without_v3_body(self, client: DataImportClientLive, payload_path: Path) -> None:
        response = _response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, text="Payload Too Large")
        with patch(f"{MODULE}.requests.post", return_value=response):
            with pytest.raises(DataImportPayloadTooLargeError) as exc_info:
                client.post_import(payload_path, "user@example.org")
        assert exc_info.value.size is None
        assert exc_info.value.max_size is None
        assert "Payload Too Large" not in exc_info.value.message

    def test_payload_too_large_without_details(self, client: DataImportClientLive, payload_path: Path) -> None:
        body = _v3_error("payload_too_large", {})
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, body)):
            with pytest.raises(DataImportPayloadTooLargeError) as exc_info:
                client.post_import(payload_path, "user@example.org")
        assert exc_info.value.size is None
        assert exc_info.value.max_size is None

    def test_import_exists(self, client: DataImportClientLive, payload_path: Path) -> None:
        body = _v3_error("import_exists", {"id": "import-456", "projectIri": PROJECT_IRI})
        with patch(f"{MODULE}.requests.post", return_value=_response(HTTPStatus.CONFLICT, body)):
            with pytest.raises(DataImportExistsError) as exc_info:
                client.post_import(payload_path, "user@example.org")
        assert exc_info.value.import_id == "import-456"
        assert exc_info.value.project_iri == PROJECT_IRI

    def test_get_status_import_not_found(self, client: DataImportClientLive) -> None:
        body = _v3_error("import_not_found", {"id": "import-123", "projectIri": PROJECT_IRI})
        with patch(f"{MODULE}.requests.get", return_value=_response(HTTPStatus.NOT_FOUND, body)):
            with pytest.raises(DataImportNotFoundError) as exc_info:
                client.get_status(IMPORT_ID)
        assert exc_info.value.import_id == "import-123"

    @pytest.mark.parametrize(
        ("status_code", "body", "expected_error"),
        [
            (HTTPStatus.FORBIDDEN, None, BadCredentialsError),
            (HTTPStatus.NOT_FOUND, _v3_error("project_not_found", {"id": PROJECT_IRI}), ProjectNotFoundError),
        ],
    )
    def test_get_status_error_types(
        self,
        client: DataImportClientLive,
        status_code: int,
        body: dict[str, Any] | None,
        expected_error: type[Exception],
    ) -> None:
        with patch(f"{MODULE}.requests.get", return_value=_response(status_code, body)):
            with pytest.raises(expected_error):
                client.get_status(IMPORT_ID)

    @pytest.mark.parametrize(
        ("status_code", "body", "expected_error"),
        [
            (HTTPStatus.FORBIDDEN, None, BadCredentialsError),
            (HTTPStatus.NOT_FOUND, _v3_error("project_not_found", {"id": PROJECT_IRI}), ProjectNotFoundError),
        ],
    )
    def test_delete_import_error_types(
        self,
        client: DataImportClientLive,
        status_code: int,
        body: dict[str, Any] | None,
        expected_error: type[Exception],
    ) -> None:
        with patch(f"{MODULE}.requests.delete", return_value=_response(status_code, body)):
            with pytest.raises(expected_error):
                client.delete_import(IMPORT_ID)

    def test_delete_import_not_found(self, client: DataImportClientLive) -> None:
        body = _v3_error("import_not_found", {"id": "import-123", "projectIri": PROJECT_IRI})
        with patch(f"{MODULE}.requests.delete", return_value=_response(HTTPStatus.NOT_FOUND, body)):
            with pytest.raises(DataImportNotFoundError) as exc_info:
                client.delete_import(IMPORT_ID)
        assert exc_info.value.import_id == "import-123"

    def test_delete_import_in_progress(self, client: DataImportClientLive) -> None:
        body = _v3_error("import_in_progress", {"id": "import-123", "projectIri": PROJECT_IRI})
        with patch(f"{MODULE}.requests.delete", return_value=_response(HTTPStatus.CONFLICT, body)):
            with pytest.raises(DataImportInProgressError) as exc_info:
                client.delete_import(IMPORT_ID)
        assert exc_info.value.import_id == "import-123"


class TestNetworkErrors:
    def test_post_import(self, client: DataImportClientLive, payload_path: Path) -> None:
        with patch(f"{MODULE}.requests.post", side_effect=RequestException("connection reset")):
            with pytest.raises(DspApiRequestError):
                client.post_import(payload_path, "user@example.org")

    def test_get_status(self, client: DataImportClientLive) -> None:
        with patch(f"{MODULE}.requests.get", side_effect=RequestException("connection reset")):
            with pytest.raises(DspApiRequestError):
                client.get_status(IMPORT_ID)

    def test_delete_import(self, client: DataImportClientLive) -> None:
        with patch(f"{MODULE}.requests.delete", side_effect=RequestException("connection reset")):
            with pytest.raises(DspApiRequestError):
                client.delete_import(IMPORT_ID)
