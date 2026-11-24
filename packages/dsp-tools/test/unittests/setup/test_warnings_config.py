import warnings
from collections.abc import Iterator

import pytest

from dsp_tools.setup.warnings_config import initialize_warnings
from dsp_vre.clients.client_warnings import DspVreUnexpectedStatusCodeWarning


@pytest.fixture
def custom_showwarning() -> Iterator[None]:
    original = warnings.showwarning
    initialize_warnings()
    yield
    warnings.showwarning = original


@pytest.mark.usefixtures("custom_showwarning")
def test_vre_unexpected_status_code_warning_prints_as_error(capsys: pytest.CaptureFixture[str]) -> None:
    warnings.showwarning("status 418", DspVreUnexpectedStatusCodeWarning, "file.py", 1)
    assert "ERROR: status 418" in capsys.readouterr().out
