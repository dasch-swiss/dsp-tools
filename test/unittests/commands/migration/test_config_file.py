from pathlib import Path

import pytest

from dsp_tools.commands.migration.config_file import create_migration_config


class TestCreateConfig:
    def test_creates_file(self, tmp_path: Path) -> None:
        result = create_migration_config(shortcode="0806", cwd=tmp_path)
        assert result is True
        assert (tmp_path / "migration-0806.yaml").exists()

    def test_file_content(self, tmp_path: Path) -> None:
        create_migration_config(shortcode="0806", cwd=tmp_path)
        content = (tmp_path / "migration-0806.yaml").read_text(encoding="utf-8")
        assert "shortcode: 0806" in content

    def test_aborts_if_file_exists(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        (tmp_path / "migration-0806.yaml").write_text("existing content", encoding="utf-8")
        result = create_migration_config(shortcode="0806", cwd=tmp_path)
        assert result is False
        assert (tmp_path / "migration-0806.yaml").read_text(encoding="utf-8") == "existing content"
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "already exists" in captured.out
