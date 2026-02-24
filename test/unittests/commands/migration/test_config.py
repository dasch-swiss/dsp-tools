from pathlib import Path

import pytest

from dsp_tools.commands.migration.config import create_migration_config


def test_creates_file(tmp_path: Path) -> None:
    result = create_migration_config(shortcode="0806", cwd=tmp_path)
    assert result is True
    assert (tmp_path / "migration-0806.yaml").exists()


def test_file_content(tmp_path: Path) -> None:
    create_migration_config(shortcode="0806", cwd=tmp_path)
    content = (tmp_path / "migration-0806.yaml").read_text(encoding="utf-8")
    assert "shortcode: 0806" in content
    assert "export-savepath: ~/.dsp-tools/migration" in content
    assert "source-server:" in content
    assert "target-server:" in content
    assert "keep-local-export: false" in content


def test_fields_are_empty_except_defaults(tmp_path: Path) -> None:
    create_migration_config(shortcode="0806", cwd=tmp_path)
    content = (tmp_path / "migration-0806.yaml").read_text(encoding="utf-8")
    lines = content.splitlines()
    empty_keys = ["server", "user", "password"]
    for line in lines:
        for key in empty_keys:
            if line.strip().startswith(f"{key}:"):
                assert line.strip() == f"{key}:", f"Expected '{key}:' to be empty but got: {line!r}"


def test_aborts_if_file_exists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "migration-0806.yaml").write_text("existing content", encoding="utf-8")
    result = create_migration_config(shortcode="0806", cwd=tmp_path)
    assert result is False
    assert (tmp_path / "migration-0806.yaml").read_text(encoding="utf-8") == "existing content"
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "already exists" in captured.out
