from unittest.mock import patch

import pytest
from packaging.version import parse

from dsp_tools.cli import entry_point

# installed 17.0.0 < latest 18.0.0, and the base versions differ -> triggers the "Continue anyway?" branch
OUTDATED_BASE_VERSION = (parse("17.0.0"), parse("18.0.0"))


def test_outdated_base_version_continues_without_prompt_when_non_interactive(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch.object(entry_point, "_get_dsp_tools_versions", return_value=OUTDATED_BASE_VERSION):
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=False):
            with patch("builtins.input", side_effect=AssertionError("input() must not be called")):
                entry_point._check_version()
    out = capsys.readouterr().out
    assert "17.0.0" in out
    assert "18.0.0" in out


def test_outdated_base_version_prompts_and_continues_on_yes() -> None:
    with patch.object(entry_point, "_get_dsp_tools_versions", return_value=OUTDATED_BASE_VERSION):
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=True):
            with patch("builtins.input", return_value="y"):
                entry_point._check_version()


def test_outdated_base_version_prompts_and_exits_on_no() -> None:
    with patch.object(entry_point, "_get_dsp_tools_versions", return_value=OUTDATED_BASE_VERSION):
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=True):
            with patch("builtins.input", return_value="n"):
                with pytest.raises(SystemExit) as exc_info:
                    entry_point._check_version()
    assert exc_info.value.code == 1
