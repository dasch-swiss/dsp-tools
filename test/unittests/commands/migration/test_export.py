from unittest.mock import MagicMock

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.commands.migration.export import _check_export_progress
from dsp_tools.commands.migration.export import _execute_export

TEST_SLEEP = 0


class TestExecuteExport:
    def test_calls_post_export_and_returns_result(self) -> None:
        export_id = ExportId("test-id-123")
        client = MagicMock()
        client.post_export.return_value = export_id
        # since this is immediately completed we do not need to mock the sleep time
        client.get_status.return_value = ExportImportStatus.COMPLETED
        success, returned_id = _execute_export(client)
        client.post_export.assert_called_once()
        client.client.get_status.assert_called_once()
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
