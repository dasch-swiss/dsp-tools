import stat
from pathlib import Path

import pytest

from dsp_tools.commands.mapping.config_file import create_mapping_config
from dsp_tools.commands.mapping.config_file import parse_mapping_config
from dsp_tools.commands.mapping.exceptions import InvalidMappingConfigFile


def test_create_config_creates_file_with_0600_permissions(tmp_path: Path) -> None:
    result = create_mapping_config(shortcode="0001", ontology="my-onto", cwd=tmp_path)
    assert result is True
    config_file = tmp_path / "mapping-0001-my-onto.yaml"
    assert config_file.exists()
    mode = stat.S_IMODE(config_file.stat().st_mode)
    assert mode == 0o600


def test_create_config_contains_all_six_fields(tmp_path: Path) -> None:
    create_mapping_config(shortcode="0001", ontology="my-onto", cwd=tmp_path)
    content = (tmp_path / "mapping-0001-my-onto.yaml").read_text()
    for field in ("shortcode", "ontology", "server", "user", "password", "excel-file"):
        assert field in content


def test_create_config_aborts_if_file_exists(tmp_path: Path) -> None:
    (tmp_path / "mapping-0001-my-onto.yaml").write_text("existing")
    result = create_mapping_config(shortcode="0001", ontology="my-onto", cwd=tmp_path)
    assert result is False
    assert (tmp_path / "mapping-0001-my-onto.yaml").read_text() == "existing"


def test_parse_config_success(tmp_path: Path) -> None:
    config_file = tmp_path / "mapping.yaml"
    config_file.write_text(
        "shortcode: '0001'\n"
        "ontology: my-onto\n"
        "server: http://localhost:3333\n"
        "user: root@example.com\n"
        "password: test\n"
        "excel-file: mappings.xlsx\n"
    )
    info = parse_mapping_config(config_file)
    assert info.config.shortcode == "0001"
    assert info.config.ontology == "my-onto"
    assert info.config.excel_file == Path("mappings.xlsx")
    assert info.server.server == "http://localhost:3333"
    assert info.server.user == "root@example.com"
    assert info.server.password == "test"


def test_parse_config_missing_field_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "mapping.yaml"
    config_file.write_text(
        "shortcode: '0001'\n"
        "ontology: my-onto\n"
        "server: http://localhost:3333\n"
        "user: root@example.com\n"
        # password is missing
        "excel-file: mappings.xlsx\n"
    )
    with pytest.raises(InvalidMappingConfigFile, match="password"):
        parse_mapping_config(config_file)
