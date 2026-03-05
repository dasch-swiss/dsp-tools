"""
This purposefully only tests the orchestration, no detailed failure is tested because that is covered in other tests.
"""

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.commands.migration.exceptions import MigrationDownloadFailureError
from dsp_tools.commands.migration.exceptions import MigrationExportFailureError
from dsp_tools.commands.migration.exceptions import MigrationImportFailureError
from dsp_tools.commands.migration.migration import _export_and_download
from dsp_tools.commands.migration.migration import _import
from dsp_tools.commands.migration.migration import migration
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo

PROJECT_IRI = "http://rdfh.ch/projects/0001"
EXPORT_ID = ExportId("export-abc")
IMPORT_ID = ImportId("import-xyz")

SOURCE = ServerInfo(server="https://src.example.com", user="src-admin", password="src-secret")
TARGET = ServerInfo(server="https://tgt.example.com", user="tgt-admin", password="tgt-secret")


@pytest.fixture
def config(tmp_path: Path) -> MigrationConfig:
    return MigrationConfig(
        shortcode="0001",
        export_savepath=tmp_path / "export-0001.zip",
        reference_savepath=tmp_path / "migration-references-0001.json",
        keep_local_export=False,
    )


@pytest.fixture
def migration_info(config: MigrationConfig) -> MigrationInfo:
    return MigrationInfo(config=config, source=SOURCE, target=TARGET)


class TestMigration:
    def test_happy_path(self, migration_info: MigrationInfo) -> None:
        with (
            patch(
                "dsp_tools.commands.migration.migration._export_and_download", return_value=PROJECT_IRI
            ) as mock_export,
            patch("dsp_tools.commands.migration.migration._import") as mock_import,
            patch("dsp_tools.commands.migration.migration.handle_local_clean_up") as mock_cleanup,
        ):
            result = migration(migration_info)

        assert result is True
        mock_export.assert_called_once_with(migration_info)
        mock_import.assert_called_once_with(migration_info, PROJECT_IRI)
        mock_cleanup.assert_called_once_with(migration_info.config)

    def test_export_and_download_raises_propagates(self, migration_info: MigrationInfo) -> None:
        with (
            patch(
                "dsp_tools.commands.migration.migration._export_and_download",
                side_effect=MigrationExportFailureError(),
            ),
            patch("dsp_tools.commands.migration.migration._import") as mock_import,
            patch("dsp_tools.commands.migration.migration.handle_local_clean_up") as mock_cleanup,
        ):
            with pytest.raises(MigrationExportFailureError):
                migration(migration_info)

        mock_import.assert_not_called()
        mock_cleanup.assert_not_called()

    def test_import_raises_propagates(self, migration_info: MigrationInfo) -> None:
        with (
            patch("dsp_tools.commands.migration.migration._export_and_download", return_value=PROJECT_IRI),
            patch(
                "dsp_tools.commands.migration.migration._import",
                side_effect=MigrationImportFailureError(),
            ),
            patch("dsp_tools.commands.migration.migration.handle_local_clean_up") as mock_cleanup,
        ):
            with pytest.raises(MigrationImportFailureError):
                migration(migration_info)

        mock_cleanup.assert_not_called()


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
                "dsp_tools.commands.migration.migration.AuthenticationClientLive",
                return_value=mock_auth,
            ),
            "project_cls": patch(
                "dsp_tools.commands.migration.migration.ProjectClientLive",
                return_value=mock_project_client,
            ),
            "export_cls": patch(
                "dsp_tools.commands.migration.migration.MigrationExportClientLive",
                return_value=mock_export_client,
            ),
            "execute_export": patch(
                "dsp_tools.commands.migration.migration.execute_export",
                return_value=export_result,
            ),
            "execute_download": patch(
                "dsp_tools.commands.migration.migration.execute_download",
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
            patches["execute_export"],
            patches["execute_download"],
        ):
            result = _export_and_download(migration_info)

        assert result == PROJECT_IRI
        mock_export_client.delete_export.assert_called_once_with(EXPORT_ID)

    def test_export_fails_does_not_call_execute_download(self, migration_info: MigrationInfo) -> None:
        patches, _, _, _ = self._make_patches(export_result=(False, EXPORT_ID))
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["execute_export"],
            patches["execute_download"] as mock_download,
        ):
            with pytest.raises(MigrationExportFailureError):
                _export_and_download(migration_info)

        mock_download.assert_not_called()

    def test_export_fails_does_not_call_delete_export(self, migration_info: MigrationInfo) -> None:
        patches, _, _, mock_export_client = self._make_patches(export_result=(False, EXPORT_ID))
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["execute_export"],
            patches["execute_download"],
        ):
            with pytest.raises(MigrationExportFailureError):
                _export_and_download(migration_info)

        mock_export_client.delete_export.assert_not_called()

    def test_download_fails_does_not_call_delete_export(self, migration_info: MigrationInfo) -> None:
        patches, _, _, mock_export_client = self._make_patches(download_result=False)
        with (
            patches["auth_cls"],
            patches["project_cls"],
            patches["export_cls"],
            patches["execute_export"],
            patches["execute_download"],
        ):
            with pytest.raises(MigrationDownloadFailureError):
                _export_and_download(migration_info)

        mock_export_client.delete_export.assert_not_called()


class TestImport:
    def _make_patches(
        self,
        import_result: tuple[bool, ImportId] = (True, IMPORT_ID),
    ):
        mock_auth = MagicMock()
        mock_import_client = MagicMock()

        patches = {
            "auth_cls": patch(
                "dsp_tools.commands.migration.migration.AuthenticationClientLive",
                return_value=mock_auth,
            ),
            "import_cls": patch(
                "dsp_tools.commands.migration.migration.MigrationImportClientLive",
                return_value=mock_import_client,
            ),
            "execute_import": patch(
                "dsp_tools.commands.migration.migration.execute_import",
                return_value=import_result,
            ),
        }
        return patches, mock_auth, mock_import_client

    def test_happy_path(self, migration_info: MigrationInfo) -> None:
        patches, _, mock_import_client = self._make_patches()
        with (
            patches["auth_cls"],
            patches["import_cls"],
            patches["execute_import"],
        ):
            _import(migration_info, PROJECT_IRI)

        mock_import_client.delete_import.assert_called_once_with(IMPORT_ID)

    def test_import_fails_does_not_call_delete_import(self, migration_info: MigrationInfo) -> None:
        patches, _, mock_import_client = self._make_patches(import_result=(False, IMPORT_ID))
        with (
            patches["auth_cls"],
            patches["import_cls"],
            patches["execute_import"],
        ):
            with pytest.raises(MigrationImportFailureError):
                _import(migration_info, PROJECT_IRI)

        mock_import_client.delete_import.assert_not_called()
