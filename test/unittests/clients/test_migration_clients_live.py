from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests
from requests import JSONDecodeError

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.migration_clients_live import MigrationImportClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.exceptions import DspToolsRequestException


@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def project_iri() -> str:
    return "http://rdfh.ch/projects/0001"


@pytest.fixture
def mock_auth_client() -> Mock:
    mock = Mock(spec=AuthenticationClient)
    mock.server = "http://0.0.0.0:3333"
    mock.get_token.return_value = "test-token-123"
    return mock


@pytest.fixture
def export_client(api_url: str, project_iri: str, mock_auth_client: Mock) -> MigrationExportClientLive:
    return MigrationExportClientLive(server=api_url, project_iri=project_iri, auth=mock_auth_client)


@pytest.fixture
def import_client(api_url: str, project_iri: str, mock_auth_client: Mock) -> MigrationImportClientLive:
    return MigrationImportClientLive(server=api_url, project_iri=project_iri, auth=mock_auth_client)


class TestMigrationExportClientLive:
    def test_post_export_success(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.ACCEPTED, ok=True, headers={})
        mock_response.json.return_value = {"id": "export-123", "status": "in_progress"}
        with patch("dsp_tools.clients.migration_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = export_client.post_export()
        assert result == ExportId("export-123")
        assert "http%3A%2F%2Frdfh.ch%2Fprojects%2F0001" in mock_post.call_args.kwargs["url"]

    def test_post_export_forbidden(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                export_client.post_export()

    def test_post_export_server_error(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                export_client.post_export()

    def test_post_export_request_exception(self, export_client: MigrationExportClientLive) -> None:
        with patch(
            "dsp_tools.clients.migration_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                export_client.post_export()

    def test_get_status_success(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={})
        mock_response.json.return_value = {"id": "export-123", "status": "completed"}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            result = export_client.get_status(ExportId("export-123"))
        assert result == ExportImportStatus.COMPLETED

    def test_get_status_in_progress(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={})
        mock_response.json.return_value = {"id": "export-123", "status": "in_progress"}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            result = export_client.get_status(ExportId("export-123"))
        assert result == ExportImportStatus.IN_PROGRESS

    def test_get_status_failed(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={})
        mock_response.json.return_value = {"id": "export-123", "status": "failed"}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            result = export_client.get_status(ExportId("export-123"))
        assert result == ExportImportStatus.FAILED

    def test_get_status_forbidden(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                export_client.get_status(ExportId("export-123"))

    def test_get_status_server_error(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                export_client.get_status(ExportId("export-123"))

    def test_get_download_success(self, export_client: MigrationExportClientLive, tmp_path: Path) -> None:
        destination = tmp_path / "export.zip"
        zip_content = b"fake zip content"
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={}, content=zip_content)
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            export_client.get_download(ExportId("export-123"), destination)
        assert destination.exists()
        assert destination.read_bytes() == zip_content

    def test_get_download_forbidden(self, export_client: MigrationExportClientLive, tmp_path: Path) -> None:
        destination = tmp_path / "export.zip"
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                export_client.get_download(ExportId("export-123"), destination)

    def test_get_download_server_error(self, export_client: MigrationExportClientLive, tmp_path: Path) -> None:
        destination = tmp_path / "export.zip"
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                export_client.get_download(ExportId("export-123"), destination)

    def test_delete_export_success(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.NO_CONTENT, ok=True, headers={}, text="")
        mock_response.json.side_effect = JSONDecodeError("No JSON", "", 0)
        with patch("dsp_tools.clients.migration_clients_live.requests.delete", return_value=mock_response):
            export_client.delete_export(ExportId("export-123"))

    def test_delete_export_forbidden(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        mock_response.json.side_effect = JSONDecodeError("No JSON", "", 0)
        with patch("dsp_tools.clients.migration_clients_live.requests.delete", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                export_client.delete_export(ExportId("export-123"))

    def test_delete_export_server_error(self, export_client: MigrationExportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        mock_response.json.side_effect = JSONDecodeError("No JSON", "", 0)
        with patch("dsp_tools.clients.migration_clients_live.requests.delete", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                export_client.delete_export(ExportId("export-123"))


class TestMigrationImportClientLive:
    def test_post_import_success(self, import_client: MigrationImportClientLive, tmp_path: Path) -> None:
        zip_file = tmp_path / "import.zip"
        zip_file.write_bytes(b"fake zip content")
        mock_response = Mock(status_code=HTTPStatus.ACCEPTED, ok=True, headers={})
        mock_response.json.return_value = {"id": "import-456", "status": "in_progress"}
        with patch("dsp_tools.clients.migration_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = import_client.post_import(zip_file)
        assert result == ImportId("import-456")
        assert mock_post.call_args.kwargs["headers"]["Content-Type"] == "application/zip"
        assert "http%3A%2F%2Frdfh.ch%2Fprojects%2F0001" in mock_post.call_args.kwargs["url"]

    def test_post_import_forbidden(self, import_client: MigrationImportClientLive, tmp_path: Path) -> None:
        zip_file = tmp_path / "import.zip"
        zip_file.write_bytes(b"fake zip content")
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                import_client.post_import(zip_file)

    def test_post_import_server_error(self, import_client: MigrationImportClientLive, tmp_path: Path) -> None:
        zip_file = tmp_path / "import.zip"
        zip_file.write_bytes(b"fake zip content")
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                import_client.post_import(zip_file)

    def test_post_import_request_exception(self, import_client: MigrationImportClientLive, tmp_path: Path) -> None:
        zip_file = tmp_path / "import.zip"
        zip_file.write_bytes(b"fake zip content")
        with patch(
            "dsp_tools.clients.migration_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                import_client.post_import(zip_file)

    def test_get_status_success(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={})
        mock_response.json.return_value = {"id": "import-456", "status": "completed"}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            result = import_client.get_status(ImportId("import-456"))
        assert result == ExportImportStatus.COMPLETED

    def test_get_status_in_progress(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={})
        mock_response.json.return_value = {"id": "import-456", "status": "in_progress"}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            result = import_client.get_status(ImportId("import-456"))
        assert result == ExportImportStatus.IN_PROGRESS

    def test_get_status_failed(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True, headers={})
        mock_response.json.return_value = {"id": "import-456", "status": "failed"}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            result = import_client.get_status(ImportId("import-456"))
        assert result == ExportImportStatus.FAILED

    def test_get_status_forbidden(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                import_client.get_status(ImportId("import-456"))

    def test_get_status_server_error(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.migration_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                import_client.get_status(ImportId("import-456"))

    def test_delete_import_success(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.NO_CONTENT, ok=True, headers={}, text="")
        mock_response.json.side_effect = JSONDecodeError("No JSON", "", 0)
        with patch("dsp_tools.clients.migration_clients_live.requests.delete", return_value=mock_response):
            import_client.delete_import(ImportId("import-456"))

    def test_delete_import_forbidden(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False, headers={}, text="Forbidden")
        mock_response.json.side_effect = JSONDecodeError("No JSON", "", 0)
        with patch("dsp_tools.clients.migration_clients_live.requests.delete", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                import_client.delete_import(ImportId("import-456"))

    def test_delete_import_server_error(self, import_client: MigrationImportClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, ok=False, headers={}, text="Server Error")
        mock_response.json.side_effect = JSONDecodeError("No JSON", "", 0)
        with patch("dsp_tools.clients.migration_clients_live.requests.delete", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                import_client.delete_import(ImportId("import-456"))


if __name__ == "__main__":
    pytest.main([__file__])
