from pathlib import Path
from typing import Any

import pytest
import yaml

from dsp_tools.commands.migration.config_file import create_migration_config
from dsp_tools.commands.migration.config_file import parse_config_file
from dsp_tools.error.exceptions import UserError
from dsp_tools.error.exceptions import UserFilepathNotFoundError


class TestParseConfigFile:
    def _write_yaml(self, tmp_path: Path, content: dict[str, Any]) -> Path:
        filepath = tmp_path / "migration.yaml"
        filepath.write_text(yaml.dump(content), encoding="utf-8")
        return filepath

    def test_complete_valid_config(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(
            tmp_path,
            {
                "shortcode": "0806",
                "source-server": [{"server": "https://src.example.com"}, {"user": "admin"}, {"password": "srcpass"}],
                "target-server": [{"server": "https://tgt.example.com"}, {"user": "admin"}, {"password": "tgtpass"}],
                "keep-local-export": False,
                "export-savepath": str(tmp_path / "export"),
            },
        )
        result = parse_config_file(filepath)
        assert result.config.shortcode == "0806"
        assert result.config.keep_local_export is False
        assert result.config.export_savepath == tmp_path / "export"
        assert result.source is not None
        assert result.source.server == "https://src.example.com"
        assert result.source.user == "admin"
        assert result.source.password == "srcpass"
        assert result.target is not None
        assert result.target.server == "https://tgt.example.com"

    def test_tilde_in_savepath_is_expanded(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(
            tmp_path,
            {
                "shortcode": "0806",
                "export-savepath": "~/foo/bar",
            },
        )
        result = parse_config_file(filepath)
        assert "~" not in str(result.config.export_savepath)
        assert result.config.export_savepath == Path("~/foo/bar").expanduser()

    def test_keep_local_export_true(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(
            tmp_path,
            {
                "shortcode": "0806",
                "keep-local-export": True,
            },
        )
        result = parse_config_file(filepath)
        assert result.config.keep_local_export is True

    def test_server_sections_absent(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(tmp_path, {"shortcode": "0806"})
        result = parse_config_file(filepath)
        assert result.source is None
        assert result.target is None

    def test_template_defaults_empty_values(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(
            tmp_path,
            {
                "shortcode": "0806",
                "source-server": [{"server": None}, {"user": None}, {"password": None}],
                "target-server": [{"server": None}, {"user": None}, {"password": None}],
            },
        )
        result = parse_config_file(filepath)
        assert result.source is None
        assert result.target is None

    def test_partial_server_info_raises(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(
            tmp_path,
            {
                "shortcode": "0806",
                "source-server": [{"server": "https://src.example.com"}, {"user": None}, {"password": None}],
            },
        )
        with pytest.raises(UserError):
            parse_config_file(filepath)

    def test_missing_shortcode_raises(self, tmp_path: Path) -> None:
        filepath = self._write_yaml(tmp_path, {"keep-local-export": False})
        with pytest.raises(UserError):
            parse_config_file(filepath)

    def test_file_not_found_raises(self, tmp_path: Path) -> None:
        with pytest.raises(UserFilepathNotFoundError):
            parse_config_file(tmp_path / "nonexistent.yaml")

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        filepath = tmp_path / "bad.yaml"
        filepath.write_text("key: [unclosed bracket", encoding="utf-8")
        with pytest.raises(UserError):
            parse_config_file(filepath)


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
