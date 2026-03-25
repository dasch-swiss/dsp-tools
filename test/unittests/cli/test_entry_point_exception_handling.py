from collections.abc import Iterator
from unittest.mock import patch

import pytest

from dsp_tools.cli import entry_point
from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


@pytest.fixture(autouse=True)
def skip_version_check() -> Iterator[None]:
    with patch("dsp_tools.cli.entry_point._check_version"):
        yield


def _run_catching_interrupts(args: list[str]) -> BaseException:
    try:
        entry_point.run(args)
    except (SystemExit, KeyboardInterrupt) as exc:
        return exc
    raise AssertionError("Expected SystemExit or KeyboardInterrupt, but run() returned normally")


def test_keyboard_interrupt_exits_130() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=KeyboardInterrupt):
        exc = _run_catching_interrupts(["excel2json", "some/path", "out.json"])
    assert isinstance(exc, SystemExit), f"Expected SystemExit, got {type(exc).__name__}"
    assert exc.code == 130  # noqa: PLR2004 (POSIX convention: exit with 128 + signal number; Ctrl+C=SIGINT=2)


def test_keyboard_interrupt_logs_info() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=KeyboardInterrupt):
        with patch("dsp_tools.cli.entry_point.logger.info") as mock_info:
            _run_catching_interrupts(["excel2json", "some/path", "out.json"])
    calls = [str(c) for c in mock_info.call_args_list]
    assert any("User interrupted execution" in c for c in calls)


def test_user_error_exits_1() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=UserError("bad input")):
        with pytest.raises(SystemExit) as exc_info:
            entry_point.run(["excel2json", "some/path", "out.json"])
    assert exc_info.value.code == 1


def test_user_error_logs_exception() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=UserError("bad input")):
        with patch("dsp_tools.cli.entry_point.logger.exception") as mock_exc:
            with pytest.raises(SystemExit):
                entry_point.run(["excel2json", "some/path", "out.json"])
    assert mock_exc.called


def test_user_error_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=UserError("bad input")):
        with pytest.raises(SystemExit):
            entry_point.run(["excel2json", "some/path", "out.json"])
    captured = capsys.readouterr()
    assert "bad input" in captured.out


def test_internal_error_exits_1() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=InternalError("something broke")):
        with pytest.raises(SystemExit) as exc_info:
            entry_point.run(["excel2json", "some/path", "out.json"])
    assert exc_info.value.code == 1


def test_internal_error_logs_exception() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=InternalError("something broke")):
        with patch("dsp_tools.cli.entry_point.logger.exception") as mock_exc:
            with pytest.raises(SystemExit):
                entry_point.run(["excel2json", "some/path", "out.json"])
    assert mock_exc.called


def test_internal_error_prints_internal_error_message(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=InternalError("something broke")):
        with pytest.raises(SystemExit):
            entry_point.run(["excel2json", "some/path", "out.json"])
    captured = capsys.readouterr()
    assert "internal error" in captured.out.lower()
    assert "something broke" in captured.out


def test_plain_exception_exits_1() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=RuntimeError("unexpected")):
        with pytest.raises(SystemExit) as exc_info:
            entry_point.run(["excel2json", "some/path", "out.json"])
    assert exc_info.value.code == 1


def test_plain_exception_logs_exception() -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=RuntimeError("unexpected")):
        with patch("dsp_tools.cli.entry_point.logger.exception") as mock_exc:
            with pytest.raises(SystemExit):
                entry_point.run(["excel2json", "some/path", "out.json"])
    assert mock_exc.called


def test_plain_exception_prints_internal_error_with_message(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("dsp_tools.cli.entry_point.call_requested_action", side_effect=RuntimeError("unexpected boom")):
        with pytest.raises(SystemExit):
            entry_point.run(["excel2json", "some/path", "out.json"])
    captured = capsys.readouterr()
    assert "unexpected boom" in captured.out
