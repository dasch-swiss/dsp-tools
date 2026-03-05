from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.commands.migration.exceptions import MigrationDownloadFailureError
from dsp_tools.commands.migration.exceptions import MigrationExportFailureError
from dsp_tools.commands.migration.export_download import _check_export_progress
from dsp_tools.commands.migration.export_download import _execute_download
from dsp_tools.commands.migration.export_download import _execute_export
from dsp_tools.commands.migration.export_download import export_and_download
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo

TEST_SLEEP = 0


def _make_config(tmp_path: Path) -> MigrationConfig:
    return MigrationConfig(
        shortcode="0001",
        export_savepath=tmp_path / "export-0001.zip",
        reference_savepath=tmp_path / "migration-references-0001.json",
        keep_local_export=False,
    )


PROJECT_IRI = "http://rdfh.ch/projects/0001"
EXPORT_ID = ExportId("export-abc")


@pytest.fixture
def migration_info(tmp_path: Path) -> MigrationInfo:
    return MigrationInfo(
        config=_make_config(tmp_path),
        source=ServerInfo(server="https://src.example.com", user="src-admin", password="src-secret"),
        target=None,
    )


class TestExportDownload:
    def _make_patches(
        self,
        export_result: tuple[bool, ExportId] = (True, EXPORT_ID),
        download_result: bool = True,
        project_iri: str = PROJECT_IRI,
    ):
        mock_auth = MagicMock()
        mock_project_client = MagicMock()
        mock_project_client.get_project_iri.return_value = project_iri
        mock_export_client = MagicMock()
        mock_export_client.project_iri = project_iri

        patches = {
            "auth_cls": patch(
                "dsp_tools.commands.migration.export_download.AuthenticationClientLive",
                return_value=mock_auth,
            ),
            "project_cls": patch(
                "dsp_tools.commands.migration.export_download.ProjectClientLive",
                return_value=mock_project_client,
            ),
            "export_cls": patch(
                "dsp_tools.commands.migration.export_download.MigrationExportClientLive",
                return_value=mock_export_client,
            ),
            "_execute_export": patch(
                "dsp_tools.commands.migration.export_download._execute_export",
                return_value=export_result,
            ),
            "_execute_download": patch(
                "dsp_tools.commands.migration.export_download._execute_download",
                return_value=download_result,
            ),
        }
        return patches, mock_auth, mock_project_client, mock_export_client

    def test_happy_path(self, migration_info: MigrationInfo) -> None:
        patches, _, _, mock_export_client = self._make_patches()
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["_execute_export"],
            patches["_execute_download"],
        ):
            result = export_and_download(migration_info)

        assert result == PROJECT_IRI
        mock_export_client.delete_export.assert_called_once_with(EXPORT_ID)

    def test_export_fails_does_not_call_execute_download(self, migration_info: MigrationInfo) -> None:
        patches, _, _, _ = self._make_patches(export_result=(False, EXPORT_ID))
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["_execute_export"],
            patches["_execute_download"] as mock_download,
        ):
            with pytest.raises(MigrationExportFailureError):
                export_and_download(migration_info)

        mock_download.assert_not_called()

    def test_export_fails_does_not_call_delete_export(self, migration_info: MigrationInfo) -> None:
        patches, _, _, mock_export_client = self._make_patches(export_result=(False, EXPORT_ID))
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["_execute_export"],
            patches["_execute_download"],
        ):
            with pytest.raises(MigrationExportFailureError):
                export_and_download(migration_info)

        mock_export_client.delete_export.assert_not_called()

    def test_download_fails_does_not_call_delete_export(self, migration_info: MigrationInfo) -> None:
        patches, _, _, mock_export_client = self._make_patches(download_result=False)
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["_execute_export"],
            patches["_execute_download"],
        ):
            with pytest.raises(MigrationDownloadFailureError):
                export_and_download(migration_info)

        mock_export_client.delete_export.assert_not_called()


class TestExecuteExport:
    def test_calls_post_export_and_returns_result(self, tmp_path: Path) -> None:
        reference_path = tmp_path / "migration-references.json"
        export_id = ExportId("test-id-123")
        client = MagicMock()
        client.project_iri = PROJECT_IRI
        client.post_export.return_value = export_id
        # since this is immediately completed we do not need to mock the sleep time
        client.get_status.return_value = ExportImportStatus.COMPLETED
        success, returned_id = _execute_export(client, reference_path)
        client.post_export.assert_called_once()
        client.get_status.assert_called_once()
        assert success is True
        assert returned_id == export_id


class TestCheckExportProgress:
    def test_completed_immediately(self) -> None:
        export_id = ExportId("test-id")
        client = MagicMock()
        client.get_status.return_value = ExportImportStatus.COMPLETED
        result = _check_export_progress(client, export_id, TEST_SLEEP)
        assert result is True

    def test_in_progress_then_completed(self) -> None:
        export_id = ExportId("test-id")
        client = MagicMock()
        client.get_status.side_effect = [
            ExportImportStatus.IN_PROGRESS,
            ExportImportStatus.IN_PROGRESS,
            ExportImportStatus.COMPLETED,
        ]
        result = _check_export_progress(client, export_id, TEST_SLEEP)
        assert result is True

    def test_failed_immediately(self) -> None:
        export_id = ExportId("test-id")
        client = MagicMock()
        client.get_status.return_value = ExportImportStatus.FAILED
        result = _check_export_progress(client, export_id, TEST_SLEEP)
        assert result is False

    def test_in_progress_then_failed(self) -> None:
        export_id = ExportId("test-id")
        client = MagicMock()
        client.get_status.side_effect = [ExportImportStatus.IN_PROGRESS, ExportImportStatus.FAILED]
        result = _check_export_progress(client, export_id, TEST_SLEEP)
        assert result is False


class TestExecuteDownload:
    def test_returns_true_on_success(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        export_id = ExportId("test-id-123")
        client = MagicMock()
        client.project_iri = "http://rdfh.ch/projects/abc"
        result = _execute_download(client, export_id, config)
        client.get_download.assert_called_once_with(export_id, config.export_savepath)
        assert result is True
