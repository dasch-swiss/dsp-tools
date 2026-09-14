import logging
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator


def test_docker_command_failure_logs_once_and_suppresses_the_original_traceback(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (tmp_path / "data.ttl").touch()
    (tmp_path / "shapes.ttl").touch()
    file_paths = ValidationFilePaths(
        directory=tmp_path, data_file="data.ttl", shacl_file="shapes.ttl", report_file="report.ttl"
    )
    called_process_error = subprocess.CalledProcessError(returncode=1, cmd=["docker"], output="stdout", stderr="stderr")
    with patch.object(ShaclCliValidator, "_run_validate_cli", side_effect=called_process_error):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ShaclValidationCliError) as exc_info:
                ShaclCliValidator().validate(file_paths)
    assert len(caplog.records) == 1
    # `from None` must suppress the chain so the original CalledProcessError's traceback
    # isn't rendered a second time wherever this exception is eventually logged upstream
    assert exc_info.value.__suppress_context__ is True
    assert exc_info.value.__cause__ is None
