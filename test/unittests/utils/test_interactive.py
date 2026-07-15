from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.error.exceptions import UserError
from dsp_tools.utils.interactive import prompt_for_required_value
from dsp_tools.utils.interactive import prompt_until_valid_answer
from dsp_tools.utils.interactive import stdin_is_interactive


class TestStdinIsInteractive:
    def test_true_when_tty(self) -> None:
        fake = Mock()
        fake.isatty.return_value = True
        with patch("dsp_tools.utils.interactive.sys.stdin", fake):
            assert stdin_is_interactive() is True

    def test_false_when_not_tty(self) -> None:
        fake = Mock()
        fake.isatty.return_value = False
        with patch("dsp_tools.utils.interactive.sys.stdin", fake):
            assert stdin_is_interactive() is False

    def test_false_when_stdin_is_none(self) -> None:
        with patch("dsp_tools.utils.interactive.sys.stdin", None):
            assert stdin_is_interactive() is False

    def test_false_when_isatty_raises(self) -> None:
        fake = Mock()
        fake.isatty.side_effect = ValueError("I/O operation on closed file")
        with patch("dsp_tools.utils.interactive.sys.stdin", fake):
            assert stdin_is_interactive() is False


class TestPromptUntilValidAnswer:
    def test_returns_non_interactive_answer_without_prompting(self, capsys: pytest.CaptureFixture[str]) -> None:
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=False):
            with patch("builtins.input", side_effect=AssertionError("must not prompt")):
                result = prompt_until_valid_answer(
                    prompt="ignored",
                    valid_answers=["y", "n"],
                    non_interactive_answer="y",
                    non_interactive_notice="proceeding without prompt",
                )
        assert result == "y"
        assert "proceeding without prompt" in capsys.readouterr().out

    def test_prompts_until_valid_when_interactive(self) -> None:
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=True):
            with patch("builtins.input", side_effect=["maybe", "n"]):
                result = prompt_until_valid_answer(
                    prompt="continue? ",
                    valid_answers=["y", "n"],
                    non_interactive_answer="y",
                    non_interactive_notice="unused",
                )
        assert result == "n"


class TestPromptForRequiredValue:
    def test_raises_useful_error_when_non_interactive(self) -> None:
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=False):
            with pytest.raises(UserError) as exc_info:
                prompt_for_required_value("project shortcode", "--project_shortcode")
        assert "--project_shortcode" in exc_info.value.message

    def test_returns_stripped_input_when_interactive(self) -> None:
        with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=True):
            with patch("builtins.input", return_value="  0ABC  "):
                assert prompt_for_required_value("project shortcode", "--project_shortcode") == "0ABC"
