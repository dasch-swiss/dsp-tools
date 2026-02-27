from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.commands.migration.exceptions import ExportZipNotFoundError
from dsp_tools.commands.migration.import_zip import _check_import_progress
from dsp_tools.commands.migration.import_zip import _execute_import
from dsp_tools.commands.migration.models import MigrationConfig

TEST_SLEEP = 0
SHORTCODE = "0099"


class TestExecuteImport:
    def test_raises_if_zip_not_found(self, tmp_path: Path) -> None:
        config = MigrationConfig(shortcode=SHORTCODE, export_savepath=tmp_path, keep_local_export=False)
        client = MagicMock()
        with pytest.raises(ExportZipNotFoundError):
            _execute_import(client, config)
        client.post_import.assert_not_called()

    def test_calls_post_import_and_returns_result(self, tmp_path: Path) -> None:
        (tmp_path / f"export-{SHORTCODE}.zip").touch()
        import_id = ImportId("test-id-123")
        config = MigrationConfig(shortcode=SHORTCODE, export_savepath=tmp_path, keep_local_export=False)
        client = MagicMock()
        client.post_import.return_value = import_id
        client.get_status.return_value = ExportImportStatus.COMPLETED
        success, returned_id = _execute_import(client, config)
        assert success is True
        assert returned_id == import_id


class TestCheckImportProgress:
    def test_completed_immediately(self) -> None:
        import_id = ImportId("test-id")
        client = MagicMock()
        client.get_status.return_value = ExportImportStatus.COMPLETED
        result = _check_import_progress(client, import_id, TEST_SLEEP)
        assert result is True

    def test_in_progress_then_completed(self) -> None:
        import_id = ImportId("test-id")
        client = MagicMock()
        client.get_status.side_effect = [
            ExportImportStatus.IN_PROGRESS,
            ExportImportStatus.IN_PROGRESS,
            ExportImportStatus.COMPLETED,
        ]
        result = _check_import_progress(client, import_id, TEST_SLEEP)
        assert result is True

    def test_failed_immediately(self) -> None:
        import_id = ImportId("test-id")
        client = MagicMock()
        client.get_status.return_value = ExportImportStatus.FAILED
        result = _check_import_progress(client, import_id, TEST_SLEEP)
        assert result is False

    def test_in_progress_then_failed(self) -> None:
        import_id = ImportId("test-id")
        client = MagicMock()
        client.get_status.side_effect = [ExportImportStatus.IN_PROGRESS, ExportImportStatus.FAILED]
        result = _check_import_progress(client, import_id, TEST_SLEEP)
        assert result is False
