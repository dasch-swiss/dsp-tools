from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.resume_xmlupload.resume_xmlupload import _skip_first_resource

STDIN_TARGET = "dsp_tools.utils.interactive.stdin_is_interactive"


class TestSkipFirstResource:
    def test_pops_first_when_pending_nonempty(self) -> None:
        state = Mock()
        state.pending_resources = ["first", "second"]
        _skip_first_resource(state)
        assert state.pending_resources == ["second"]

    def test_non_interactive_empty_pending_continues(self) -> None:
        state = Mock()
        state.pending_resources = []
        with patch(STDIN_TARGET, return_value=False):
            with patch("builtins.input", side_effect=AssertionError("input() must not be called")):
                _skip_first_resource(state)

    def test_interactive_empty_pending_no_exits(self) -> None:
        state = Mock()
        state.pending_resources = []
        with patch(STDIN_TARGET, return_value=True):
            with patch("builtins.input", return_value="n"):
                with pytest.raises(SystemExit) as exc_info:
                    _skip_first_resource(state)
        assert exc_info.value.code == 1
