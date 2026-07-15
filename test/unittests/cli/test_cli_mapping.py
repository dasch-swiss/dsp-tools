from collections.abc import Iterator
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.cli import entry_point
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.mapping.models import MappingConfig
from dsp_tools.commands.mapping.models import MappingInfo


@pytest.fixture(autouse=True)
def skip_version_check() -> Iterator[None]:
    with patch("dsp_tools.cli.entry_point._check_version"):
        yield


@patch("dsp_tools.cli.call_action_files_only.create_mapping_config")
def test_mapping_config_dispatch(create_mapping_config: Mock) -> None:
    create_mapping_config.return_value = True
    entry_point.run("mapping config -P 0001 --ontology my-onto".split())
    create_mapping_config.assert_called_once_with(
        shortcode="0001",
        ontology="my-onto",
        mapping_path=Path.cwd() / "0001-my-onto-mapping.yaml",
    )


@patch("dsp_tools.cli.call_action_files_only.create_mapping_config")
def test_mapping_config_prompts_when_interactive(create_mapping_config: Mock) -> None:
    create_mapping_config.return_value = True
    with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=True):
        with patch("builtins.input", side_effect=["0001", "my-onto"]):
            entry_point.run("mapping config".split())
    create_mapping_config.assert_called_once_with(
        shortcode="0001",
        ontology="my-onto",
        mapping_path=Path.cwd() / "0001-my-onto-mapping.yaml",
    )


@patch("dsp_tools.cli.call_action_files_only.create_mapping_config")
def test_mapping_config_errors_when_non_interactive_and_shortcode_missing(
    create_mapping_config: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=False):
        with pytest.raises(SystemExit) as exc_info:
            entry_point.run("mapping config".split())
    assert exc_info.value.code == 1
    create_mapping_config.assert_not_called()
    assert "--project-shortcode" in capsys.readouterr().out


@patch("dsp_tools.cli.utils._check_network_health")
@patch("dsp_tools.cli.call_action_with_network.mapping_add")
@patch("dsp_tools.cli.call_action_with_network.parse_mapping_config")
def test_mapping_add_dispatch(
    parse_mapping_config: Mock,
    mapping_add: Mock,
    check_network: Mock,  # noqa: ARG001
) -> None:
    config_path = "testdata/xml-data/test-data-systematic-4123.xml"  # existing file for path check
    mock_info = MappingInfo(
        config=MappingConfig(shortcode="0001", ontology="my-onto", excel_file=Path(config_path)),
        server=ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test"),
    )
    parse_mapping_config.return_value = mock_info
    mapping_add.return_value = True

    entry_point.run(f"mapping add {config_path}".split())
    parse_mapping_config.assert_called_once_with(Path(config_path))
    mapping_add.assert_called_once_with(mock_info)


def test_mapping_without_subcommand_raises() -> None:
    with pytest.raises(SystemExit) as exc_info:
        entry_point.run(["mapping"])
    assert exc_info.value.code == 1
