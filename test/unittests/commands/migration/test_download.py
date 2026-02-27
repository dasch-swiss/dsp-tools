from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.commands.migration.download import _execute_download
from dsp_tools.commands.migration.exceptions import ExportZipExistsError
from dsp_tools.commands.migration.models import MigrationConfig


def _make_config(tmp_path: Path) -> MigrationConfig:
    return MigrationConfig(
        shortcode="0001",
        export_savepath=tmp_path / "export-0001.zip",
        reference_savepath=tmp_path / "export-reference-0001.zip",
        keep_local_export=False,
    )


class TestExecuteDownload:
    def test_returns_true_on_success(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        export_id = ExportId("test-id-123")
        client = MagicMock()
        result = _execute_download(client, export_id, config)
        client.get_download.assert_called_once_with(export_id, config.export_savepath)
        assert result is True

    def test_raises_if_zip_already_exists(self, tmp_path: Path) -> None:
        config = _make_config(tmp_path)
        export_id = ExportId("test-id-123")
        (tmp_path / "export-0001.zip").touch()
        client = MagicMock()
        with pytest.raises(ExportZipExistsError):
            _execute_download(client, export_id, config)
