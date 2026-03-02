import logging
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.commands.migration.clean_up import _clean_up_source_server
from dsp_tools.commands.migration.clean_up import _clean_up_target_server
from dsp_tools.commands.migration.clean_up import _handle_local_clean_up
from dsp_tools.commands.migration.clean_up import _handle_source_server_clean_up
from dsp_tools.commands.migration.clean_up import _handle_target_server_clean_up
from dsp_tools.commands.migration.exceptions import InvalidMigrationConfigFile
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ReferenceInfo
from dsp_tools.commands.migration.models import ServerInfo

PROJECT_IRI = "http://rdfh.ch/projects/0001"


@pytest.fixture
def server_info() -> ServerInfo:
    return ServerInfo(server="https://src.example.com", user="admin", password="secret")


def _make_config(tmp_path: Path, keep_local_export: bool = False) -> MigrationConfig:
    return MigrationConfig(
        shortcode="0001",
        export_savepath=tmp_path / "export-0001.zip",
        reference_savepath=tmp_path / "migration-references-0001.json",
        keep_local_export=keep_local_export,
    )


class TestHandleLocalCleanUp:
    def test_skips_when_keep_local_export(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path, keep_local_export=True)
        config.export_savepath.touch()
        config.reference_savepath.touch()
        _handle_local_clean_up(config)
        assert config.export_savepath.exists()
        assert config.reference_savepath.exists()

    def test_deletes_both_files_when_both_exist(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        config.export_savepath.touch()
        config.reference_savepath.touch()
        _handle_local_clean_up(config)
        assert not config.export_savepath.exists()
        assert not config.reference_savepath.exists()

    def test_missing_export_savepath_logs_warning(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        config = _make_config(tmp_path)
        config.reference_savepath.touch()
        with caplog.at_level(logging.WARNING):
            _handle_local_clean_up(config)
        assert not config.reference_savepath.exists()
        assert str(config.export_savepath) in caplog.text

    def test_missing_reference_savepath_logs_warning(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        config = _make_config(tmp_path)
        config.export_savepath.touch()
        with caplog.at_level(logging.WARNING):
            _handle_local_clean_up(config)
        assert not config.export_savepath.exists()
        assert str(config.reference_savepath) in caplog.text

    def test_both_missing_logs_two_warnings(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        config = _make_config(tmp_path)
        with caplog.at_level(logging.WARNING):
            _handle_local_clean_up(config)
        assert str(config.export_savepath) in caplog.text
        assert str(config.reference_savepath) in caplog.text


class TestHandleSourceServerCleanUp:
    def test_skips_when_no_export_id(self) -> None:
        reference_info = ReferenceInfo(export_id=None, import_id=None, project_iri=PROJECT_IRI)
        with patch("dsp_tools.commands.migration.clean_up._clean_up_source_server") as mock_clean_up:
            _handle_source_server_clean_up(None, reference_info)
        mock_clean_up.assert_not_called()

    def test_calls_clean_up_source_server(self, server_info) -> None:
        reference_info = ReferenceInfo(export_id=ExportId("abc"), import_id=None, project_iri=PROJECT_IRI)
        with patch("dsp_tools.commands.migration.clean_up._clean_up_source_server") as mock_clean_up:
            _handle_source_server_clean_up(server_info, reference_info)
        mock_clean_up.assert_called_once_with(server_info, ExportId("abc"), PROJECT_IRI)


class TestHandleTargetServerCleanUp:
    def test_skips_when_no_import_id(self) -> None:
        reference_info = ReferenceInfo(export_id=None, import_id=None, project_iri=PROJECT_IRI)
        with patch("dsp_tools.commands.migration.clean_up._clean_up_target_server") as mock_clean_up:
            _handle_target_server_clean_up(None, reference_info)
        mock_clean_up.assert_not_called()


    def test_calls_clean_up_target_server(self, server_info) -> None:
        reference_info = ReferenceInfo(export_id=None, import_id=ImportId("xyz"), project_iri=PROJECT_IRI)
        with patch("dsp_tools.commands.migration.clean_up._clean_up_target_server") as mock_clean_up:
            _handle_target_server_clean_up(server_info, reference_info)
        mock_clean_up.assert_called_once_with(server_info, ImportId("xyz"), PROJECT_IRI)


class TestCleanUpSourceServer:
    def test_creates_clients_and_calls_delete_export(self, server_info) -> None:
        export_id = ExportId("abc")
        with (
            patch("dsp_tools.commands.migration.clean_up.AuthenticationClientLive") as mock_auth_cls,
            patch("dsp_tools.commands.migration.clean_up.MigrationExportClientLive") as mock_export_cls,
        ):
            mock_auth = MagicMock()
            mock_auth_cls.return_value = mock_auth
            mock_client = MagicMock()
            mock_export_cls.return_value = mock_client

            _clean_up_source_server(server_info, export_id, PROJECT_IRI)

        mock_auth_cls.assert_called_once_with(server_info.server, server_info.user, server_info.password)
        mock_export_cls.assert_called_once_with(server_info.server, PROJECT_IRI, mock_auth)
        mock_client.delete_export.assert_called_once_with(export_id)


class TestCleanUpTargetServer:
    def test_creates_clients_and_calls_delete_import(self, server_info) -> None:
        import_id = ImportId("xyz")
        with (
            patch("dsp_tools.commands.migration.clean_up.AuthenticationClientLive") as mock_auth_cls,
            patch("dsp_tools.commands.migration.clean_up.MigrationImportClientLive") as mock_import_cls,
        ):
            mock_auth = MagicMock()
            mock_auth_cls.return_value = mock_auth
            mock_client = MagicMock()
            mock_import_cls.return_value = mock_client

            _clean_up_target_server(server_info, import_id, PROJECT_IRI)

        mock_auth_cls.assert_called_once_with(server_info.server, server_info.user, server_info.password)
        mock_import_cls.assert_called_once_with(server_info.server, PROJECT_IRI, mock_auth)
        mock_client.delete_import.assert_called_once_with(import_id)
