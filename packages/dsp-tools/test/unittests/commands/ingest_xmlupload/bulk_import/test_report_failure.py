from pathlib import Path

import pytest

from dsp_tools.commands.ingest_xmlupload.bulk_import.report_failure import report_failed_import

NEXT_STEP = "Correct the XML file and run 'ingest-xmlupload' again."


@pytest.mark.parametrize("error_message", [None, ""])
def test_no_message_writes_no_file(
    error_message: str | None, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "error.txt"
    report_failed_import(error_message, target)
    assert not target.exists()
    out = capsys.readouterr().out
    assert "The server sent no error message." in out
    assert NEXT_STEP in out


def test_short_message(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "error.txt"
    report_failed_import("bad data", target)
    assert target.read_text(encoding="utf-8") == "bad data"
    out = capsys.readouterr().out
    assert "bad data" in out
    assert f"The full error message is in: {target}" in out
    assert NEXT_STEP in out
    assert "more lines" not in out


def test_long_message_prints_first_lines(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "error.txt"
    message = "\n".join(f"line {i}" for i in range(1, 16))
    report_failed_import(message, target)
    assert target.read_text(encoding="utf-8") == message
    out = capsys.readouterr().out
    assert "line 10\n" in out
    assert "line 11" not in out
    assert "(5 more lines)" in out
