from collections.abc import Iterator
from pathlib import Path

import pytest
from loguru import logger

from dsp_tools.setup import logger_config as logger_config_module

PASSWORD = "secret-test-password-4711"


@pytest.fixture
def log_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    log_path = tmp_path / "logging.log"
    monkeypatch.setattr(logger_config_module, "LOGGER_SAVEPATH", log_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DSP_TOOLS_SAVE_ADDITIONAL_LOG_FILE_IN_CWD", raising=False)
    yield log_path
    # The logger is global: restore the sinks that the other tests expect
    monkeypatch.undo()
    logger_config_module.logger_config()


def _fail_with_password_on_failing_line(password: str) -> None:
    raise ValueError(len(password))


def _log_exception_with_password_in_frame() -> None:
    try:
        _fail_with_password_on_failing_line(PASSWORD)
    except ValueError:
        logger.exception("Something failed")


def test_traceback_does_not_contain_variable_values_by_default(log_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DSP_TOOLS_LOG_VARIABLE_VALUES", raising=False)
    logger_config_module.logger_config()
    _log_exception_with_password_in_frame()
    log_content = log_file.read_text(encoding="utf-8")
    assert "_fail_with_password_on_failing_line" in log_content
    assert "ValueError" in log_content
    assert PASSWORD not in log_content


def test_traceback_contains_variable_values_if_opted_in(log_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DSP_TOOLS_LOG_VARIABLE_VALUES", "true")
    logger_config_module.logger_config()
    _log_exception_with_password_in_frame()
    log_content = log_file.read_text(encoding="utf-8")
    assert PASSWORD in log_content
