import logging
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

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


def test_records_of_dsp_vre_lib_go_into_the_log_file(log_file: Path) -> None:
    logger_config_module.logger_config()
    logging.getLogger("dsp_vre_lib.clients.some_client").debug("vre-lib debug record")
    assert "vre-lib debug record" in log_file.read_text(encoding="utf-8")


def test_repeated_configuration_adds_one_handler_to_dsp_vre_lib(log_file: Path) -> None:  # noqa: ARG001
    logger_config_module.logger_config()
    logger_config_module.logger_config()
    vre_lib_logger = logging.getLogger("dsp_vre_lib")
    intercepts = [h for h in vre_lib_logger.handlers if isinstance(h, logger_config_module._LoguruInterceptHandler)]
    assert len(intercepts) == 1


def test_notices_of_dsp_vre_lib_are_printed(log_file: Path, capsys: pytest.CaptureFixture[str]) -> None:  # noqa: ARG001
    logger_config_module.logger_config()
    logging.getLogger("dsp_vre_lib.notices").info("Kicked off the ingest process")
    logging.getLogger("dsp_vre_lib.clients.some_client").info("not a notice")
    out = capsys.readouterr().out
    assert out.endswith(": Kicked off the ingest process\n")
    assert "not a notice" not in out


def _emit_vre_lib_record() -> None:
    logging.getLogger("dsp_vre_lib.clients.some_client").warning("record with an origin")


def test_loguru_record_of_dsp_vre_lib_names_the_module_that_emitted_it(log_file: Path) -> None:  # noqa: ARG001
    logger_config_module.logger_config()
    names: list[str] = []
    sink_id = logger.add(lambda message: names.append(message.record["name"] or ""), level="WARNING")
    try:
        _emit_vre_lib_record()
    finally:
        logger.remove(sink_id)
    assert names == [__name__]


def test_failing_notice_printer_calls_handle_error(log_file: Path) -> None:  # noqa: ARG001
    handler = logger_config_module._NoticePrintHandler()
    record = logging.LogRecord("dsp_vre_lib.notices", logging.INFO, __file__, 1, "msg", None, None)
    with patch("builtins.print", side_effect=OSError("closed")), patch.object(handler, "handleError") as handle_error:
        handler.emit(record)
    handle_error.assert_called_once_with(record)


def test_failing_loguru_handler_calls_handle_error(log_file: Path) -> None:  # noqa: ARG001
    handler = logger_config_module._LoguruInterceptHandler()
    record = logging.LogRecord("dsp_vre_lib.x", logging.INFO, __file__, 1, "msg", None, None)
    with (
        patch.object(logger, "opt", side_effect=RuntimeError("broken")),
        patch.object(handler, "handleError") as handle_error,
    ):
        handler.emit(record)
    handle_error.assert_called_once_with(record)


def test_replace_handler_keeps_one_handler_of_the_type() -> None:
    target = logging.getLogger("dsp_vre_lib.test_replace_handler")
    other = logging.NullHandler()
    target.addHandler(other)
    try:
        logger_config_module._replace_handler(target.name, logging.StreamHandler())
        replacement = logging.StreamHandler()
        logger_config_module._replace_handler(target.name, replacement)
        assert target.handlers == [other, replacement]
    finally:
        target.handlers.clear()
