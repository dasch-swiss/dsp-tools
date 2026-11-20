import logging
import subprocess
import sys

from dsp_vre_lib.clients.request_utils import notify

# A fresh interpreter: other tests can configure the logging of the test process.
_WARN_WITHOUT_CONFIGURATION = """
import logging

import dsp_vre_lib.clients

logging.getLogger("dsp_vre_lib.clients.x").warning("unconfigured warning")
"""


def test_warning_without_configured_logging_writes_nothing_to_stderr() -> None:
    result = subprocess.run(
        [sys.executable, "-c", _WARN_WITHOUT_CONFIGURATION],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_notify_writes_one_notice_and_one_module_record() -> None:
    package_handler, notice_handler = _ListHandler(), _ListHandler()
    package_logger, notice_logger = logging.getLogger("dsp_vre_lib"), logging.getLogger("dsp_vre_lib.notices")
    old_level = package_logger.level
    package_logger.setLevel(logging.DEBUG)
    package_logger.addHandler(package_handler)
    notice_logger.addHandler(notice_handler)
    try:
        notify(logging.getLogger("dsp_vre_lib.clients.some_client"), "a notice", logging.WARNING)
    finally:
        package_logger.removeHandler(package_handler)
        notice_logger.removeHandler(notice_handler)
        package_logger.setLevel(old_level)
    assert [(r.name, r.levelno) for r in notice_handler.records] == [("dsp_vre_lib.notices", logging.INFO)]
    assert [(r.name, r.levelno) for r in package_handler.records] == [
        ("dsp_vre_lib.clients.some_client", logging.WARNING)
    ]
