from pathlib import Path
from unittest.mock import MagicMock

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.commands.migration.download import _execute_download
from dsp_tools.commands.migration.models import MigrationConfig


def _make_config(tmp_path: Path) -> MigrationConfig:
    return MigrationConfig(
        shortcode="0001",
        export_savepath=tmp_path / "export-0001.zip",
        reference_savepath=tmp_path / "migration-references-0001.json",
        keep_local_export=False,
    )


class TestExecuteDownload:
    def test_returns_true_on_success(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        export_id = ExportId("test-id-123")
        client = MagicMock()
        client.project_iri = "http://rdfh.ch/projects/abc"
        result = _execute_download(client, export_id, config)
        client.get_download.assert_called_once_with(export_id, config.export_savepath)
        assert result is True
