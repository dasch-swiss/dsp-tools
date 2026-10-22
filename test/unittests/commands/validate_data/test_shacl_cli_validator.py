import logging
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError
from dsp_tools.commands.validate_data.exceptions import ShaclValidationOutOfMemoryError
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


def _make_file_paths(tmp_path: Path) -> ValidationFilePaths:
    (tmp_path / "data.ttl").touch()
    (tmp_path / "shapes.ttl").touch()
    return ValidationFilePaths(
        directory=tmp_path, data_file="data.ttl", shacl_file="shapes.ttl", report_file="report.ttl"
    )


def test_docker_command_sets_the_java_options(tmp_path: Path) -> None:
    file_paths = _make_file_paths(tmp_path)
    with patch("dsp_tools.commands.validate_data.shacl_cli_validator.subprocess.run") as run:
        ShaclCliValidator()._run_validate_cli(file_paths)
    docker_args = run.call_args.args[0]
    java_opts_index = docker_args.index("JAVA_OPTS=-XX:MaxRAMPercentage=50 -XX:+ExitOnOutOfMemoryError")
    assert docker_args[java_opts_index - 1] == "-e"
    assert docker_args.index("-e") < docker_args.index("validate")


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr"),
    [
        (3, "Terminating due to java.lang.OutOfMemoryError: Java heap space", ""),
        (1, "", "Exception in thread main java.lang.OutOfMemoryError: Java heap space"),
        (137, "", ""),
    ],
)
def test_out_of_memory_raises_user_error(tmp_path: Path, returncode: int, stdout: str, stderr: str) -> None:
    file_paths = _make_file_paths(tmp_path)
    called_process_error = subprocess.CalledProcessError(returncode, cmd=["docker"], output=stdout, stderr=stderr)
    with patch.object(ShaclCliValidator, "_run_validate_cli", side_effect=called_process_error):
        with pytest.raises(ShaclValidationOutOfMemoryError, match="memory"):
            ShaclCliValidator().validate(file_paths)


def test_out_of_memory_message_names_the_docker_memory() -> None:
    assert "8.0 GB" in str(ShaclValidationOutOfMemoryError(8 * 1024**3))
    assert "GB" not in str(ShaclValidationOutOfMemoryError(None))
