import subprocess
import sys

from dsp_vre_lib.clients.request_utils import notices

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


def test_notices_do_not_propagate() -> None:
    assert notices.propagate is False
